#!/usr/bin/env python3
#
# Copyright (c) 2025 Nelson Grey LLC
# Author: Nelson Grey LLC
#
# Licensed under the Nelson Grey LLC Community License 1.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://github.com/mnelson3/sas-ci360-sol-content-delivery/blob/main/LICENSE
#
# -*- coding: utf-8 -*-
"""
SAS CI360 Content Delivery Module Base Class

Provides foundational functionality for SAS Customer Intelligence 360
content delivery operations, including connection management, authentication,
and digital asset management capabilities.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class CI360ContentDeliveryConfig:
    """Configuration for CI360 Content Delivery operations."""

    algorithm: str = "HS256"
    api_base: str = "/digital-assets"
    encoding: str = "utf-8"
    host: Optional[str] = None
    secret_key: Optional[str] = None
    tenant_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 0.5
    enable_compression: bool = True
    max_file_size_mb: int = 100
    supported_formats: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'gif', 'pdf', 'html', 'txt', 'mp4', 'avi'
    ])


class CI360ContentDeliveryError(Exception):
    """Base exception for CI360 Content Delivery operations."""
    pass


class CI360ContentDeliveryAuthError(CI360ContentDeliveryError):
    """Authentication-related errors."""
    pass


class CI360ContentDeliveryConnectionError(CI360ContentDeliveryError):
    """Connection and network-related errors."""
    pass


class CI360ContentDeliveryValidationError(CI360ContentDeliveryError):
    """Data validation errors."""
    pass


class CI360ContentDeliveryBase:
    """
    Base class for SAS CI360 Content Delivery operations.

    Provides authentication, connection management, and common functionality
    for digital asset and content management API interactions with async support.
    """

    def __init__(self, config: Optional[CI360ContentDeliveryConfig] = None) -> None:
        """
        Initialize the CI360 Content Delivery base client.

        Args:
            config: Configuration object for CI360 Content Delivery operations

        Raises:
            CI360ContentDeliveryValidationError: If required configuration is missing
        """
        self.config = config or CI360ContentDeliveryConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Validate configuration
        self._validate_config()

        # Initialize HTTP session with retry strategy
        self.session = self._create_session()

        # Generate authentication token
        self.token = self._generate_token()

        # Connection state
        self._connected = False

        self.logger.info("CI360 Content Delivery Base initialized successfully")

    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_fields = ['host', 'secret_key', 'tenant_id']
        missing = [field for field in required_fields if not getattr(self.config, field)]

        if missing:
            raise CI360ContentDeliveryValidationError(f"Missing required configuration: {', '.join(missing)}")

        # Validate algorithm
        supported_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']
        if self.config.algorithm not in supported_algorithms:
            raise CI360ContentDeliveryValidationError(f"Unsupported algorithm: {self.config.algorithm}")

        # Validate file size limit
        if self.config.max_file_size_mb <= 0:
            raise CI360ContentDeliveryValidationError("max_file_size_mb must be positive")

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _generate_token(self) -> str:
        """Generate JWT authentication token."""
        try:
            # Import here to avoid circular imports
            from sasci360apicore.encryption import Encryption

            encryption = Encryption(
                algorithm=self.config.algorithm,
                encoding=self.config.encoding
            )

            return encryption.generate_jwt(
                tenant_id=self.config.tenant_id,
                secret_key=self.config.secret_key
            )
        except Exception as e:
            raise CI360ContentDeliveryAuthError(f"Failed to generate authentication token: {e}")

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

    async def validate_connection_async(self) -> bool:
        """
        Asynchronously validate connection to CI360 service.

        Returns:
            bool: True if connection is valid
        """
        try:
            # Basic health check endpoint; config.host is validated non-None in __init__
            assert self.config.host is not None
            health_url = urljoin(self.config.host, "/health")
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
            # Run async validation in sync context
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
            CI360ContentDeliveryConnectionError: For network/connection errors
            CI360ContentDeliveryAuthError: For authentication errors
        """
        if not self._connected:
            await self.validate_connection_async()
            if not self._connected:
                raise CI360ContentDeliveryConnectionError("No active connection to CI360 service")

        assert self.config.host is not None  # validated non-None in __init__
        url = urljoin(self.config.host + self.config.api_base, endpoint.lstrip('/'))
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
                raise CI360ContentDeliveryAuthError(f"Authentication failed: {e}")
            elif response.status_code >= 500:
                raise CI360ContentDeliveryConnectionError(f"Server error: {e}")
            else:
                raise CI360ContentDeliveryError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise CI360ContentDeliveryConnectionError(f"Network error: {e}")

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

    # Digital Asset Management APIs

    async def get_assets_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve digital assets asynchronously.

        Args:
            limit: Maximum number of assets to return
            offset: Number of assets to skip
            filters: Optional filters for assets

        Returns:
            Dict containing asset data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/assets", params=params)

    def get_assets(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve digital assets synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/assets", params=params)

    async def get_asset_async(self, asset_id: str) -> Dict[str, Any]:
        """
        Retrieve specific asset data asynchronously.

        Args:
            asset_id: Unique asset identifier

        Returns:
            Dict containing asset data
        """
        return await self._make_request_async("GET", f"/assets/{asset_id}")

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Retrieve specific asset data synchronously."""
        return self._make_request("GET", f"/assets/{asset_id}")

    async def upload_asset_async(self, asset_data: Dict[str, Any], file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Upload new digital asset asynchronously.

        Args:
            asset_data: Asset metadata
            file_content: Binary file content
            filename: Original filename

        Returns:
            Dict containing uploaded asset data
        """
        # For file uploads, we'd typically use multipart/form-data
        # This is a simplified implementation - in practice, you'd use requests-toolbelt or similar
        import io
        from requests_toolbelt.multipart.encoder import MultipartEncoder

        # Create multipart form data
        fields = {
            'metadata': ('metadata', str(asset_data), 'application/json'),
            'file': (filename, io.BytesIO(file_content), 'application/octet-stream')
        }

        encoder = MultipartEncoder(fields=fields)
        headers = self.get_auth_headers()
        headers['Content-Type'] = encoder.content_type

        assert self.config.host is not None  # validated non-None in __init__
        url = urljoin(self.config.host + self.config.api_base, "/assets/upload")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.session.post(
                url,
                data=encoder,
                headers=headers,
                timeout=self.config.timeout
            )
        )

        response.raise_for_status()
        return response.json() if response.content else {}

    def upload_asset(self, asset_data: Dict[str, Any], file_content: bytes, filename: str) -> Dict[str, Any]:
        """Upload new digital asset synchronously."""
        try:
            return asyncio.run(self.upload_asset_async(asset_data, file_content, filename))
        except Exception as e:
            self.logger.error(f"Asset upload failed: {e}")
            raise

    async def update_asset_async(self, asset_id: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update asset metadata asynchronously.

        Args:
            asset_id: Unique asset identifier
            asset_data: Updated asset metadata

        Returns:
            Dict containing updated asset data
        """
        return await self._make_request_async("PUT", f"/assets/{asset_id}", data=asset_data)

    def update_asset(self, asset_id: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update asset metadata synchronously."""
        return self._make_request("PUT", f"/assets/{asset_id}", data=asset_data)

    async def delete_asset_async(self, asset_id: str) -> bool:
        """
        Delete digital asset asynchronously.

        Args:
            asset_id: Unique asset identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/assets/{asset_id}")
        return True

    def delete_asset(self, asset_id: str) -> bool:
        """Delete digital asset synchronously."""
        self._make_request("DELETE", f"/assets/{asset_id}")
        return True

    # Content Delivery APIs

    async def deliver_content_async(self, asset_id: str, delivery_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deliver content to specified channels asynchronously.

        Args:
            asset_id: Unique asset identifier
            delivery_config: Delivery configuration (channels, recipients, etc.)

        Returns:
            Dict containing delivery results
        """
        payload = {
            "assetId": asset_id,
            "deliveryConfig": delivery_config
        }
        return await self._make_request_async("POST", "/delivery/send", data=payload)

    def deliver_content(self, asset_id: str, delivery_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver content to specified channels synchronously."""
        payload = {
            "assetId": asset_id,
            "deliveryConfig": delivery_config
        }
        return self._make_request("POST", "/delivery/send", data=payload)

    async def get_delivery_status_async(self, delivery_id: str) -> Dict[str, Any]:
        """
        Get content delivery status asynchronously.

        Args:
            delivery_id: Unique delivery identifier

        Returns:
            Dict containing delivery status and details
        """
        return await self._make_request_async("GET", f"/delivery/{delivery_id}")

    def get_delivery_status(self, delivery_id: str) -> Dict[str, Any]:
        """Get content delivery status synchronously."""
        return self._make_request("GET", f"/delivery/{delivery_id}")

    async def get_deliveries_async(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List content deliveries asynchronously.

        Args:
            limit: Maximum number of deliveries to return
            offset: Number of deliveries to skip
            status_filter: Optional status filter (pending, sent, failed, delivered)

        Returns:
            Dict containing list of deliveries
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if status_filter:
            params["status"] = status_filter

        return await self._make_request_async("GET", "/delivery", params=params)

    def get_deliveries(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List content deliveries synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if status_filter:
            params["status"] = status_filter

        return self._make_request("GET", "/delivery", params=params)

    # Content Templates APIs

    async def get_content_templates_async(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve content templates asynchronously.

        Args:
            category: Optional template category filter
            limit: Maximum number of templates to return
            offset: Number of templates to skip

        Returns:
            Dict containing content templates
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return await self._make_request_async("GET", "/templates/content", params=params)

    def get_content_templates(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve content templates synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return self._make_request("GET", "/templates/content", params=params)

    async def create_content_from_template_async(self, template_id: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content from template asynchronously.

        Args:
            template_id: Unique template identifier
            content_data: Content-specific configuration

        Returns:
            Dict containing created content data
        """
        payload = {
            "templateId": template_id,
            "contentData": content_data
        }
        return await self._make_request_async("POST", "/content/from-template", data=payload)

    def create_content_from_template(self, template_id: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create content from template synchronously."""
        payload = {
            "templateId": template_id,
            "contentData": content_data
        }
        return self._make_request("POST", "/content/from-template", data=payload)

    # Content Analytics APIs

    async def get_content_analytics_async(
        self,
        asset_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get content delivery analytics asynchronously.

        Args:
            asset_id: Optional asset filter
            start_date: Start date for analytics (ISO format)
            end_date: End date for analytics (ISO format)

        Returns:
            Dict containing content analytics
        """
        params = {}
        if asset_id:
            params["assetId"] = asset_id
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        return await self._make_request_async("GET", "/analytics/content", params=params)

    def get_content_analytics(
        self,
        asset_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get content delivery analytics synchronously."""
        params = {}
        if asset_id:
            params["assetId"] = asset_id
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        return self._make_request("GET", "/analytics/content", params=params)

    def __enter__(self):
        """Context manager entry."""
        if not self.validate_connection():
            raise CI360ContentDeliveryConnectionError("Failed to establish connection")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.validate_connection_async():
            raise CI360ContentDeliveryConnectionError("Failed to establish connection")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.session.close()
