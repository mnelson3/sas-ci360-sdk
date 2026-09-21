#!/usr/bin/env python3
#
# Copyright (c) 2025 Nelson Grey LLC
# Author: Nelson Grey LLC
#
# Licensed under the Nelson Grey LLC Community License 1.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://github.com/mnelson3/sas-ci360-sdk/blob/main/LICENSE
#
# -*- coding: utf-8 -*-
"""
Shared REST client base for every CI360 domain package (sol-data, sol-execute,
sol-workflow, sol-planning, sol-content-delivery, sol-identity).

Each domain package's Config subclasses RestClientConfig (adding only its own
extra fields) and its Base subclasses RestClientBase (adding only its own
domain methods), setting the 4 `_..._CLS` class attributes so the shared
code raises that package's own exception classes.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sasci360apicore.encryption import Encryption

SUPPORTED_ALGORITHMS = ("HS256", "HS384", "HS512", "RS256", "RS384", "RS512")


@dataclass
class RestClientConfig:
    """Configuration shared by every CI360 REST client."""

    algorithm: str = "HS256"
    api_base: str = ""
    encoding: str = "utf-8"
    host: Optional[str] = None
    secret_key: Optional[str] = None
    tenant_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 0.5
    enable_compression: bool = True


class RestClientError(Exception):
    """Base exception for CI360 REST client operations."""
    pass


class RestClientAuthError(RestClientError):
    """Authentication-related errors."""
    pass


class RestClientConnectionError(RestClientError):
    """Connection and network-related errors."""
    pass


class RestClientValidationError(RestClientError):
    """Configuration/data validation errors."""
    pass


class RestClientBase:
    """
    Base class for CI360 REST clients: JWT authentication, a retrying HTTP
    session, connection validation, and request dispatch, with sync and
    async forms of every operation.

    A subclass must set `_CONFIG_CLS` to its own Config dataclass and
    `_ERROR_CLS`, `_AUTH_ERROR_CLS`, `_CONNECTION_ERROR_CLS`, and
    `_VALIDATION_ERROR_CLS` to its own exception classes. It may override
    `_validate_extra_config()` to add config checks beyond the shared
    required-fields/algorithm check, and `_health_check_url()` if connection
    validation shouldn't hit the default bare `/health` endpoint.
    """

    _CONFIG_CLS = RestClientConfig
    _ERROR_CLS = RestClientError
    _AUTH_ERROR_CLS = RestClientAuthError
    _CONNECTION_ERROR_CLS = RestClientConnectionError
    _VALIDATION_ERROR_CLS = RestClientValidationError

    def __init__(self, config: Optional[RestClientConfig] = None) -> None:
        """
        Initialize the REST client.

        Args:
            config: Configuration object for this client

        Raises:
            The subclass's validation error: if required configuration is missing
        """
        self.config = config or self._CONFIG_CLS()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Validate configuration
        self._validate_config()

        # Initialize HTTP session with retry strategy
        self.session = self._create_session()

        # Generate authentication token
        self.token = self._generate_token()

        # Connection state
        self._connected = False

        self.logger.info("%s initialized successfully", self.__class__.__name__)

    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_fields = ["host", "secret_key", "tenant_id"]
        missing = [f for f in required_fields if not getattr(self.config, f)]

        if missing:
            raise self._VALIDATION_ERROR_CLS(f"Missing required configuration: {', '.join(missing)}")

        if self.config.algorithm not in SUPPORTED_ALGORITHMS:
            raise self._VALIDATION_ERROR_CLS(f"Unsupported algorithm: {self.config.algorithm}")

        self._validate_extra_config()

    def _validate_extra_config(self) -> None:
        """Hook for a subclass's own config checks beyond the shared ones. No-op by default."""
        pass

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @property
    def _base_url(self) -> str:
        """Base URL for CI360 API requests (host is validated as non-None in __init__)."""
        assert self.config.host is not None
        return self.config.host.rstrip("/") + self.config.api_base

    def _generate_token(self) -> str:
        """Generate JWT authentication token."""
        try:
            encryption = Encryption(
                algorithm=self.config.algorithm,
                encoding=self.config.encoding
            )

            token = encryption.generate_jwt(
                tenant_id=self.config.tenant_id,
                secret_key=self.config.secret_key
            )
        except Exception as e:
            raise self._AUTH_ERROR_CLS(f"Failed to generate authentication token: {e}")

        if token is None:
            raise self._AUTH_ERROR_CLS("Failed to generate authentication token: encryption.generate_jwt returned None")

        return token

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dict[str, str]: Headers dictionary with authorization token
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tenant-ID": str(self.config.tenant_id)
        }

    def _health_check_url(self) -> str:
        """URL connection validation checks. Overridable for a domain whose API
        doesn't expose a bare /health endpoint (e.g. SCIM's ServiceProviderConfig)."""
        assert self.config.host is not None
        return urljoin(self.config.host, "/health")

    async def validate_connection_async(self) -> bool:
        """
        Asynchronously validate connection to CI360 service.

        Returns:
            bool: True if connection is valid
        """
        try:
            health_url = self._health_check_url()
            headers = self.get_auth_headers()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(
                    health_url,
                    headers=headers,
                    timeout=self.config.timeout
                )
            )

            self._connected = response.status_code == 200
            return self._connected

        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            self._connected = False
            return False

    def validate_connection(self) -> bool:
        """
        Validate connection to CI360 service.

        Returns:
            bool: True if connection is valid
        """
        try:
            return asyncio.run(self.validate_connection_async())
        except Exception as e:
            self.logger.error(f"Sync connection validation failed: {e}")
            return False

    async def _make_request_async(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make asynchronous HTTP request to CI360 API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Dict[str, Any]: Response data

        Raises:
            The subclass's connection/auth/generic error classes
        """
        if not self._connected:
            await self.validate_connection_async()
            if not self._connected:
                raise self._CONNECTION_ERROR_CLS("No active connection to CI360 service")

        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        headers = self.get_auth_headers()

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=self.config.timeout
                )
            )

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise self._AUTH_ERROR_CLS(f"Authentication failed: {e}")
            elif response.status_code >= 500:
                raise self._CONNECTION_ERROR_CLS(f"Server error: {e}")
            else:
                raise self._ERROR_CLS(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise self._CONNECTION_ERROR_CLS(f"Network error: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make synchronous HTTP request to CI360 API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Dict[str, Any]: Response data
        """
        try:
            return asyncio.run(self._make_request_async(method, endpoint, data, params))
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        if not self.validate_connection():
            raise self._CONNECTION_ERROR_CLS("Failed to establish connection")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.validate_connection_async():
            raise self._CONNECTION_ERROR_CLS("Failed to establish connection")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.session.close()


if __name__ == "__main__":
    pass
