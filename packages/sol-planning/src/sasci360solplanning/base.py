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
SAS CI360 Planning Module Base Class

Provides the Plan API's client, built on sasci360apicore.rest_client's
shared connection/auth/request handling.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from sasci360apicore.rest_client import RestClientBase, RestClientConfig


@dataclass
class CI360PlanningConfig(RestClientConfig):
    """Configuration for CI360 Planning operations."""

    api_base: str = "/marketingPlanning"
    max_campaigns_per_user: int = 100
    max_audience_size: int = 1000000


class CI360PlanningError(Exception):
    """Base exception for CI360 Planning operations."""
    pass


class CI360PlanningAuthError(CI360PlanningError):
    """Authentication-related errors."""
    pass


class CI360PlanningConnectionError(CI360PlanningError):
    """Connection and network-related errors."""
    pass


class CI360PlanningValidationError(CI360PlanningError):
    """Data validation errors."""
    pass


class CI360PlanningBase(RestClientBase):
    """
    Client for SAS CI360 Planning operations.

    Provides authentication, connection management, and common functionality
    for marketing planning and campaign management API interactions with async support.
    """

    _CONFIG_CLS = CI360PlanningConfig
    _ERROR_CLS = CI360PlanningError
    _AUTH_ERROR_CLS = CI360PlanningAuthError
    _CONNECTION_ERROR_CLS = CI360PlanningConnectionError
    _VALIDATION_ERROR_CLS = CI360PlanningValidationError

    def _validate_extra_config(self) -> None:
        if self.config.max_campaigns_per_user <= 0:
            raise CI360PlanningValidationError("max_campaigns_per_user must be positive")

    # Campaign Management APIs

    async def get_campaigns_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve campaigns asynchronously.

        Args:
            limit: Maximum number of campaigns to return
            offset: Number of campaigns to skip
            filters: Optional filters for campaigns

        Returns:
            Dict containing campaign data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/campaigns", params=params)

    def get_campaigns(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve campaigns synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/campaigns", params=params)

    async def get_campaign_async(self, campaign_id: str) -> Dict[str, Any]:
        """
        Retrieve specific campaign data asynchronously.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            Dict containing campaign data
        """
        return await self._make_request_async("GET", f"/campaigns/{campaign_id}")

    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Retrieve specific campaign data synchronously."""
        return self._make_request("GET", f"/campaigns/{campaign_id}")

    async def create_campaign_async(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new campaign asynchronously.

        Args:
            campaign_data: Campaign configuration data

        Returns:
            Dict containing created campaign data
        """
        return await self._make_request_async("POST", "/campaigns", data=campaign_data)

    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new campaign synchronously."""
        return self._make_request("POST", "/campaigns", data=campaign_data)

    async def update_campaign_async(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update campaign data asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            campaign_data: Updated campaign data

        Returns:
            Dict containing updated campaign data
        """
        return await self._make_request_async("PUT", f"/campaigns/{campaign_id}", data=campaign_data)

    def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign data synchronously."""
        return self._make_request("PUT", f"/campaigns/{campaign_id}", data=campaign_data)

    async def delete_campaign_async(self, campaign_id: str) -> bool:
        """
        Delete campaign asynchronously.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/campaigns/{campaign_id}")
        return True

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete campaign synchronously."""
        self._make_request("DELETE", f"/campaigns/{campaign_id}")
        return True

    # Audience Targeting APIs

    async def get_audiences_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve audiences asynchronously.

        Args:
            limit: Maximum number of audiences to return
            offset: Number of audiences to skip
            filters: Optional filters for audiences

        Returns:
            Dict containing audience data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/audiences", params=params)

    def get_audiences(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve audiences synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/audiences", params=params)

    async def get_audience_async(self, audience_id: str) -> Dict[str, Any]:
        """
        Retrieve specific audience data asynchronously.

        Args:
            audience_id: Unique audience identifier

        Returns:
            Dict containing audience data
        """
        return await self._make_request_async("GET", f"/audiences/{audience_id}")

    def get_audience(self, audience_id: str) -> Dict[str, Any]:
        """Retrieve specific audience data synchronously."""
        return self._make_request("GET", f"/audiences/{audience_id}")

    async def create_audience_async(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new audience asynchronously.

        Args:
            audience_data: Audience definition data

        Returns:
            Dict containing created audience data
        """
        return await self._make_request_async("POST", "/audiences", data=audience_data)

    def create_audience(self, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new audience synchronously."""
        return self._make_request("POST", "/audiences", data=audience_data)

    async def update_audience_async(self, audience_id: str, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update audience definition asynchronously.

        Args:
            audience_id: Unique audience identifier
            audience_data: Updated audience data

        Returns:
            Dict containing updated audience data
        """
        return await self._make_request_async("PUT", f"/audiences/{audience_id}", data=audience_data)

    def update_audience(self, audience_id: str, audience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update audience definition synchronously."""
        return self._make_request("PUT", f"/audiences/{audience_id}", data=audience_data)

    async def delete_audience_async(self, audience_id: str) -> bool:
        """
        Delete audience asynchronously.

        Args:
            audience_id: Unique audience identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/audiences/{audience_id}")
        return True

    def delete_audience(self, audience_id: str) -> bool:
        """Delete audience synchronously."""
        self._make_request("DELETE", f"/audiences/{audience_id}")
        return True

    async def estimate_audience_size_async(self, audience_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate audience size based on criteria asynchronously.

        Args:
            audience_criteria: Audience targeting criteria

        Returns:
            Dict containing audience size estimate
        """
        return await self._make_request_async("POST", "/audiences/estimate", data=audience_criteria)

    def estimate_audience_size(self, audience_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate audience size based on criteria synchronously."""
        return self._make_request("POST", "/audiences/estimate", data=audience_criteria)

    # Campaign Optimization APIs

    async def optimize_campaign_async(
        self,
        campaign_id: str,
        optimization_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize campaign performance asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            optimization_params: Optional optimization parameters

        Returns:
            Dict containing optimization recommendations
        """
        payload = {
            "campaignId": campaign_id,
            "optimizationParams": optimization_params or {}
        }
        return await self._make_request_async("POST", "/campaigns/optimize", data=payload)

    def optimize_campaign(self, campaign_id: str, optimization_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize campaign performance synchronously."""
        payload = {
            "campaignId": campaign_id,
            "optimizationParams": optimization_params or {}
        }
        return self._make_request("POST", "/campaigns/optimize", data=payload)

    async def get_campaign_analytics_async(
        self,
        campaign_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get campaign analytics asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            start_date: Start date for analytics (ISO format)
            end_date: End date for analytics (ISO format)

        Returns:
            Dict containing campaign analytics
        """
        params = {"campaignId": campaign_id}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        return await self._make_request_async("GET", "/analytics/campaigns", params=params)

    def get_campaign_analytics(
        self,
        campaign_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get campaign analytics synchronously."""
        params = {"campaignId": campaign_id}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        return self._make_request("GET", "/analytics/campaigns", params=params)

    # Campaign Templates APIs

    async def get_campaign_templates_async(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve campaign templates asynchronously.

        Args:
            category: Optional template category filter
            limit: Maximum number of templates to return
            offset: Number of templates to skip

        Returns:
            Dict containing campaign templates
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return await self._make_request_async("GET", "/templates/campaigns", params=params)

    def get_campaign_templates(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve campaign templates synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return self._make_request("GET", "/templates/campaigns", params=params)

    async def create_campaign_from_template_async(self, template_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create campaign from template asynchronously.

        Args:
            template_id: Unique template identifier
            campaign_data: Campaign-specific configuration

        Returns:
            Dict containing created campaign data
        """
        payload = {
            "templateId": template_id,
            "campaignData": campaign_data
        }
        return await self._make_request_async("POST", "/campaigns/from-template", data=payload)

    def create_campaign_from_template(self, template_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create campaign from template synchronously."""
        payload = {
            "templateId": template_id,
            "campaignData": campaign_data
        }
        return self._make_request("POST", "/campaigns/from-template", data=payload)
