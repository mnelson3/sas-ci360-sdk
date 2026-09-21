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
SAS CI360 Identity Module Base Class

Provides the SCIM API's client, built on sasci360apicore.rest_client's
shared connection/auth/request handling.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sasci360apicore.rest_client import RestClientBase, RestClientConfig


@dataclass
class CI360IdentityConfig(RestClientConfig):
    """Configuration for CI360 Identity operations."""

    api_base: str = "/scim"
    scim_version: str = "2.0"


class CI360IdentityError(Exception):
    """Base exception for CI360 Identity operations."""
    pass


class CI360IdentityAuthError(CI360IdentityError):
    """Authentication-related errors."""
    pass


class CI360IdentityConnectionError(CI360IdentityError):
    """Connection and network-related errors."""
    pass


class CI360IdentityValidationError(CI360IdentityError):
    """Data validation errors."""
    pass


class CI360IdentityBase(RestClientBase):
    """
    Client for SAS CI360 Identity operations.

    Provides authentication, connection management, and common functionality
    for identity and user management API interactions using SCIM with async support.
    """

    _CONFIG_CLS = CI360IdentityConfig
    _ERROR_CLS = CI360IdentityError
    _AUTH_ERROR_CLS = CI360IdentityAuthError
    _CONNECTION_ERROR_CLS = CI360IdentityConnectionError
    _VALIDATION_ERROR_CLS = CI360IdentityValidationError

    def _validate_extra_config(self) -> None:
        supported_versions = ['2.0', '1.1']
        if self.config.scim_version not in supported_versions:
            raise CI360IdentityValidationError(f"Unsupported SCIM version: {self.config.scim_version}")

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dict[str, str]: Headers dictionary with authorization token
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/scim+json",
            "Accept": "application/scim+json",
            "X-Tenant-ID": str(self.config.tenant_id),
            "SCIM-Version": self.config.scim_version
        }

    def _health_check_url(self) -> str:
        """SCIM has no bare /health endpoint; ServiceProviderConfig is its
        equivalent well-known, unauthenticated-shape discovery endpoint."""
        return f"{self._base_url.rstrip('/')}/ServiceProviderConfig"

    # User Management APIs

    async def get_users_async(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve users asynchronously.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            filters: Optional filters for users

        Returns:
            Dict containing user data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/Users", params=params)

    def get_users(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve users synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/Users", params=params)

    async def get_user_async(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve specific user data asynchronously.

        Args:
            user_id: Unique user identifier

        Returns:
            Dict containing user data
        """
        return await self._make_request_async("GET", f"/Users/{user_id}")

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Retrieve specific user data synchronously."""
        return self._make_request("GET", f"/Users/{user_id}")

    async def create_user_async(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user asynchronously.

        Args:
            user_data: User data to create

        Returns:
            Dict containing created user data
        """
        return await self._make_request_async("POST", "/Users", data=user_data)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user synchronously."""
        return self._make_request("POST", "/Users", data=user_data)

    async def update_user_async(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user data asynchronously.

        Args:
            user_id: Unique user identifier
            user_data: Updated user data

        Returns:
            Dict containing updated user data
        """
        return await self._make_request_async("PUT", f"/Users/{user_id}", data=user_data)

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data synchronously."""
        return self._make_request("PUT", f"/Users/{user_id}", data=user_data)

    async def patch_user_async(self, user_id: str, patch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Patch user data asynchronously (SCIM patch operation).

        Args:
            user_id: Unique user identifier
            patch_data: SCIM patch operations

        Returns:
            Dict containing updated user data
        """
        return await self._make_request_async("PATCH", f"/Users/{user_id}", data=patch_data)

    def patch_user(self, user_id: str, patch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Patch user data synchronously (SCIM patch operation)."""
        return self._make_request("PATCH", f"/Users/{user_id}", data=patch_data)

    async def delete_user_async(self, user_id: str) -> bool:
        """
        Delete user asynchronously.

        Args:
            user_id: Unique user identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/Users/{user_id}")
        return True

    def delete_user(self, user_id: str) -> bool:
        """Delete user synchronously."""
        self._make_request("DELETE", f"/Users/{user_id}")
        return True

    # Group Management APIs

    async def get_groups_async(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve groups asynchronously.

        Args:
            limit: Maximum number of groups to return
            offset: Number of groups to skip
            filters: Optional filters for groups

        Returns:
            Dict containing group data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/Groups", params=params)

    def get_groups(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve groups synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/Groups", params=params)

    async def get_group_async(self, group_id: str) -> Dict[str, Any]:
        """
        Retrieve specific group data asynchronously.

        Args:
            group_id: Unique group identifier

        Returns:
            Dict containing group data
        """
        return await self._make_request_async("GET", f"/Groups/{group_id}")

    def get_group(self, group_id: str) -> Dict[str, Any]:
        """Retrieve specific group data synchronously."""
        return self._make_request("GET", f"/Groups/{group_id}")

    async def create_group_async(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new group asynchronously.

        Args:
            group_data: Group data to create

        Returns:
            Dict containing created group data
        """
        return await self._make_request_async("POST", "/Groups", data=group_data)

    def create_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new group synchronously."""
        return self._make_request("POST", "/Groups", data=group_data)

    async def update_group_async(self, group_id: str, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update group data asynchronously.

        Args:
            group_id: Unique group identifier
            group_data: Updated group data

        Returns:
            Dict containing updated group data
        """
        return await self._make_request_async("PUT", f"/Groups/{group_id}", data=group_data)

    def update_group(self, group_id: str, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update group data synchronously."""
        return self._make_request("PUT", f"/Groups/{group_id}", data=group_data)

    async def delete_group_async(self, group_id: str) -> bool:
        """
        Delete group asynchronously.

        Args:
            group_id: Unique group identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/Groups/{group_id}")
        return True

    def delete_group(self, group_id: str) -> bool:
        """Delete group synchronously."""
        self._make_request("DELETE", f"/Groups/{group_id}")
        return True

    # Authentication APIs

    async def authenticate_user_async(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate user asynchronously.

        Args:
            credentials: User authentication credentials

        Returns:
            Dict containing authentication result and tokens
        """
        return await self._make_request_async("POST", "/auth/authenticate", data=credentials)

    def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user synchronously."""
        return self._make_request("POST", "/auth/authenticate", data=credentials)

    async def validate_token_async(self, token: str) -> Dict[str, Any]:
        """
        Validate authentication token asynchronously.

        Args:
            token: JWT token to validate

        Returns:
            Dict containing token validation result
        """
        payload = {"token": token}
        return await self._make_request_async("POST", "/auth/validate", data=payload)

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate authentication token synchronously."""
        payload = {"token": token}
        return self._make_request("POST", "/auth/validate", data=payload)

    async def refresh_token_async(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh authentication token asynchronously.

        Args:
            refresh_token: Refresh token

        Returns:
            Dict containing new tokens
        """
        payload = {"refreshToken": refresh_token}
        return await self._make_request_async("POST", "/auth/refresh", data=payload)

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh authentication token synchronously."""
        payload = {"refreshToken": refresh_token}
        return self._make_request("POST", "/auth/refresh", data=payload)

    # SCIM Service Provider Configuration

    async def get_service_provider_config_async(self) -> Dict[str, Any]:
        """
        Get SCIM service provider configuration asynchronously.

        Returns:
            Dict containing SCIM service provider configuration
        """
        return await self._make_request_async("GET", "/ServiceProviderConfig")

    def get_service_provider_config(self) -> Dict[str, Any]:
        """Get SCIM service provider configuration synchronously."""
        return self._make_request("GET", "/ServiceProviderConfig")

    # Bulk Operations

    async def bulk_operation_async(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform bulk SCIM operations asynchronously.

        Args:
            operations: List of SCIM bulk operations

        Returns:
            Dict containing bulk operation results
        """
        payload = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": operations
        }
        return await self._make_request_async("POST", "/Bulk", data=payload)

    def bulk_operation(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform bulk SCIM operations synchronously."""
        payload = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": operations
        }
        return self._make_request("POST", "/Bulk", data=payload)
