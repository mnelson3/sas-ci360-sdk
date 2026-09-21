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
SAS CI360 Execute Module Base Class

Provides the Marketing Execution API's client, built on
sasci360apicore.rest_client's shared connection/auth/request handling.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from sasci360apicore.rest_client import RestClientBase, RestClientConfig


@dataclass
class CI360ExecuteConfig(RestClientConfig):
    """Configuration for CI360 Execute operations."""

    api_base: str = "/marketingExecution"
    batch_size: int = 1000
    max_concurrent_jobs: int = 10
    job_timeout: int = 3600


class CI360ExecuteError(Exception):
    """Base exception for CI360 Execute operations."""
    pass


class CI360ExecuteAuthError(CI360ExecuteError):
    """Authentication-related errors."""
    pass


class CI360ExecuteConnectionError(CI360ExecuteError):
    """Connection and network-related errors."""
    pass


class CI360ExecuteValidationError(CI360ExecuteError):
    """Data validation errors."""
    pass


class CI360ExecuteBase(RestClientBase):
    """
    Client for SAS CI360 Execute operations.

    Provides authentication, connection management, and common functionality
    for campaign execution, messaging, and batch operations with async support.
    """

    _CONFIG_CLS = CI360ExecuteConfig
    _ERROR_CLS = CI360ExecuteError
    _AUTH_ERROR_CLS = CI360ExecuteAuthError
    _CONNECTION_ERROR_CLS = CI360ExecuteConnectionError
    _VALIDATION_ERROR_CLS = CI360ExecuteValidationError

    def _validate_extra_config(self) -> None:
        if self.config.batch_size <= 0:
            raise CI360ExecuteValidationError("batch_size must be positive")

    # Campaign Execution APIs

    async def execute_campaign_async(
        self,
        campaign_id: str,
        execution_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a campaign asynchronously.

        Args:
            campaign_id: Unique campaign identifier
            execution_params: Optional execution parameters

        Returns:
            Dict containing execution results and job ID
        """
        payload = {
            "campaignId": campaign_id,
            "executionParams": execution_params or {}
        }
        return await self._make_request_async("POST", "/campaigns/execute", data=payload)

    def execute_campaign(self, campaign_id: str, execution_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a campaign synchronously."""
        payload = {
            "campaignId": campaign_id,
            "executionParams": execution_params or {}
        }
        return self._make_request("POST", "/campaigns/execute", data=payload)

    async def get_execution_status_async(self, execution_id: str) -> Dict[str, Any]:
        """
        Get campaign execution status asynchronously.

        Args:
            execution_id: Unique execution identifier

        Returns:
            Dict containing execution status and details
        """
        return await self._make_request_async("GET", f"/executions/{execution_id}")

    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get campaign execution status synchronously."""
        return self._make_request("GET", f"/executions/{execution_id}")

    async def cancel_execution_async(self, execution_id: str) -> bool:
        """
        Cancel a running campaign execution asynchronously.

        Args:
            execution_id: Unique execution identifier

        Returns:
            True if cancellation successful
        """
        await self._make_request_async("POST", f"/executions/{execution_id}/cancel")
        return True

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running campaign execution synchronously."""
        self._make_request("POST", f"/executions/{execution_id}/cancel")
        return True

    # Batch Processing APIs

    async def submit_batch_job_async(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a batch job for processing asynchronously.

        Args:
            job_data: Batch job configuration and data

        Returns:
            Dict containing job submission results and job ID
        """
        return await self._make_request_async("POST", "/batch/jobs", data=job_data)

    def submit_batch_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a batch job for processing synchronously."""
        return self._make_request("POST", "/batch/jobs", data=job_data)

    async def get_batch_job_status_async(self, job_id: str) -> Dict[str, Any]:
        """
        Get batch job status asynchronously.

        Args:
            job_id: Unique batch job identifier

        Returns:
            Dict containing job status and progress
        """
        return await self._make_request_async("GET", f"/batch/jobs/{job_id}")

    def get_batch_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch job status synchronously."""
        return self._make_request("GET", f"/batch/jobs/{job_id}")

    async def cancel_batch_job_async(self, job_id: str) -> bool:
        """
        Cancel a batch job asynchronously.

        Args:
            job_id: Unique batch job identifier

        Returns:
            True if cancellation successful
        """
        await self._make_request_async("POST", f"/batch/jobs/{job_id}/cancel")
        return True

    def cancel_batch_job(self, job_id: str) -> bool:
        """Cancel a batch job synchronously."""
        self._make_request("POST", f"/batch/jobs/{job_id}/cancel")
        return True

    async def get_batch_jobs_async(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List batch jobs asynchronously.

        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            status_filter: Optional status filter (pending, running, completed, failed)

        Returns:
            Dict containing list of batch jobs
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if status_filter:
            params["status"] = status_filter

        return await self._make_request_async("GET", "/batch/jobs", params=params)

    def get_batch_jobs(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List batch jobs synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if status_filter:
            params["status"] = status_filter

        return self._make_request("GET", "/batch/jobs", params=params)

    # Job Scheduling APIs

    async def schedule_job_async(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a job for future execution asynchronously.

        Args:
            schedule_data: Job schedule configuration

        Returns:
            Dict containing schedule creation results
        """
        return await self._make_request_async("POST", "/schedules", data=schedule_data)

    def schedule_job(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a job for future execution synchronously."""
        return self._make_request("POST", "/schedules", data=schedule_data)

    async def get_scheduled_jobs_async(
        self,
        limit: int = 50,
        offset: int = 0,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        List scheduled jobs asynchronously.

        Args:
            limit: Maximum number of schedules to return
            offset: Number of schedules to skip
            active_only: Whether to return only active schedules

        Returns:
            Dict containing list of scheduled jobs
        """
        params = {
            "limit": limit,
            "offset": offset,
            "activeOnly": active_only
        }
        return await self._make_request_async("GET", "/schedules", params=params)

    def get_scheduled_jobs(
        self,
        limit: int = 50,
        offset: int = 0,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """List scheduled jobs synchronously."""
        params = {
            "limit": limit,
            "offset": offset,
            "activeOnly": active_only
        }
        return self._make_request("GET", "/schedules", params=params)

    async def update_schedule_async(self, schedule_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a job schedule asynchronously.

        Args:
            schedule_id: Unique schedule identifier
            schedule_data: Updated schedule configuration

        Returns:
            Dict containing updated schedule
        """
        return await self._make_request_async("PUT", f"/schedules/{schedule_id}", data=schedule_data)

    def update_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a job schedule synchronously."""
        return self._make_request("PUT", f"/schedules/{schedule_id}", data=schedule_data)

    async def delete_schedule_async(self, schedule_id: str) -> bool:
        """
        Delete a job schedule asynchronously.

        Args:
            schedule_id: Unique schedule identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/schedules/{schedule_id}")
        return True

    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a job schedule synchronously."""
        self._make_request("DELETE", f"/schedules/{schedule_id}")
        return True

    # Execution Monitoring APIs

    async def get_execution_metrics_async(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get execution metrics asynchronously.

        Args:
            start_date: Start date for metrics (ISO format)
            end_date: End date for metrics (ISO format)
            campaign_id: Optional campaign filter

        Returns:
            Dict containing execution metrics
        """
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if campaign_id:
            params["campaignId"] = campaign_id

        return await self._make_request_async("GET", "/metrics/executions", params=params)

    def get_execution_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get execution metrics synchronously."""
        params = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if campaign_id:
            params["campaignId"] = campaign_id

        return self._make_request("GET", "/metrics/executions", params=params)
