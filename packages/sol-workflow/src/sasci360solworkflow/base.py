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
SAS CI360 Workflow Module Base Class

Provides the Workflow API's client, built on sasci360apicore.rest_client's
shared connection/auth/request handling.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from sasci360apicore.rest_client import RestClientBase, RestClientConfig


@dataclass
class CI360WorkflowConfig(RestClientConfig):
    """Configuration for CI360 Workflow operations."""

    api_base: str = "/marketingWorkflow"
    max_concurrent_workflows: int = 50
    workflow_timeout: int = 7200


class CI360WorkflowError(Exception):
    """Base exception for CI360 Workflow operations."""
    pass


class CI360WorkflowAuthError(CI360WorkflowError):
    """Authentication-related errors."""
    pass


class CI360WorkflowConnectionError(CI360WorkflowError):
    """Connection and network-related errors."""
    pass


class CI360WorkflowValidationError(CI360WorkflowError):
    """Data validation errors."""
    pass


class CI360WorkflowBase(RestClientBase):
    """
    Client for SAS CI360 Workflow operations.

    Provides authentication, connection management, and common functionality
    for workflow automation and process management API interactions with async support.
    """

    _CONFIG_CLS = CI360WorkflowConfig
    _ERROR_CLS = CI360WorkflowError
    _AUTH_ERROR_CLS = CI360WorkflowAuthError
    _CONNECTION_ERROR_CLS = CI360WorkflowConnectionError
    _VALIDATION_ERROR_CLS = CI360WorkflowValidationError

    def _validate_extra_config(self) -> None:
        if self.config.max_concurrent_workflows <= 0:
            raise CI360WorkflowValidationError("max_concurrent_workflows must be positive")

    # Workflow Management APIs

    async def get_workflows_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve workflows asynchronously.

        Args:
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip
            filters: Optional filters for workflows

        Returns:
            Dict containing workflow data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/workflows", params=params)

    def get_workflows(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve workflows synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/workflows", params=params)

    async def get_workflow_async(self, workflow_id: str) -> Dict[str, Any]:
        """
        Retrieve specific workflow data asynchronously.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            Dict containing workflow data
        """
        return await self._make_request_async("GET", f"/workflows/{workflow_id}")

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Retrieve specific workflow data synchronously."""
        return self._make_request("GET", f"/workflows/{workflow_id}")

    async def create_workflow_async(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new workflow asynchronously.

        Args:
            workflow_data: Workflow definition data

        Returns:
            Dict containing created workflow data
        """
        return await self._make_request_async("POST", "/workflows", data=workflow_data)

    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new workflow synchronously."""
        return self._make_request("POST", "/workflows", data=workflow_data)

    async def update_workflow_async(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update workflow definition asynchronously.

        Args:
            workflow_id: Unique workflow identifier
            workflow_data: Updated workflow data

        Returns:
            Dict containing updated workflow data
        """
        return await self._make_request_async("PUT", f"/workflows/{workflow_id}", data=workflow_data)

    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update workflow definition synchronously."""
        return self._make_request("PUT", f"/workflows/{workflow_id}", data=workflow_data)

    async def delete_workflow_async(self, workflow_id: str) -> bool:
        """
        Delete workflow asynchronously.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/workflows/{workflow_id}")
        return True

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow synchronously."""
        self._make_request("DELETE", f"/workflows/{workflow_id}")
        return True

    # Process Execution APIs

    async def start_process_async(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start workflow process execution asynchronously.

        Args:
            workflow_id: Unique workflow identifier
            input_data: Optional input data for the process

        Returns:
            Dict containing process execution results
        """
        payload = {
            "workflowId": workflow_id,
            "inputData": input_data or {}
        }
        return await self._make_request_async("POST", "/processes/start", data=payload)

    def start_process(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start workflow process execution synchronously."""
        payload = {
            "workflowId": workflow_id,
            "inputData": input_data or {}
        }
        return self._make_request("POST", "/processes/start", data=payload)

    async def get_process_status_async(self, process_id: str) -> Dict[str, Any]:
        """
        Get process execution status asynchronously.

        Args:
            process_id: Unique process identifier

        Returns:
            Dict containing process status and details
        """
        return await self._make_request_async("GET", f"/processes/{process_id}")

    def get_process_status(self, process_id: str) -> Dict[str, Any]:
        """Get process execution status synchronously."""
        return self._make_request("GET", f"/processes/{process_id}")

    async def cancel_process_async(self, process_id: str) -> bool:
        """
        Cancel running process asynchronously.

        Args:
            process_id: Unique process identifier

        Returns:
            True if cancellation successful
        """
        await self._make_request_async("POST", f"/processes/{process_id}/cancel")
        return True

    def cancel_process(self, process_id: str) -> bool:
        """Cancel running process synchronously."""
        self._make_request("POST", f"/processes/{process_id}/cancel")
        return True

    async def get_processes_async(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List process executions asynchronously.

        Args:
            limit: Maximum number of processes to return
            offset: Number of processes to skip
            status_filter: Optional status filter (running, completed, failed, cancelled)

        Returns:
            Dict containing list of process executions
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if status_filter:
            params["status"] = status_filter

        return await self._make_request_async("GET", "/processes", params=params)

    def get_processes(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List process executions synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if status_filter:
            params["status"] = status_filter

        return self._make_request("GET", "/processes", params=params)

    # Trigger Management APIs

    async def get_triggers_async(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve workflow triggers asynchronously.

        Args:
            limit: Maximum number of triggers to return
            offset: Number of triggers to skip
            filters: Optional filters for triggers

        Returns:
            Dict containing trigger data and metadata
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return await self._make_request_async("GET", "/triggers", params=params)

    def get_triggers(
        self,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve workflow triggers synchronously."""
        params = {
            "limit": limit,
            "offset": offset
        }
        if filters:
            params.update(filters)

        return self._make_request("GET", "/triggers", params=params)

    async def create_trigger_async(self, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new workflow trigger asynchronously.

        Args:
            trigger_data: Trigger configuration data

        Returns:
            Dict containing created trigger data
        """
        return await self._make_request_async("POST", "/triggers", data=trigger_data)

    def create_trigger(self, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new workflow trigger synchronously."""
        return self._make_request("POST", "/triggers", data=trigger_data)

    async def update_trigger_async(self, trigger_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update trigger configuration asynchronously.

        Args:
            trigger_id: Unique trigger identifier
            trigger_data: Updated trigger data

        Returns:
            Dict containing updated trigger data
        """
        return await self._make_request_async("PUT", f"/triggers/{trigger_id}", data=trigger_data)

    def update_trigger(self, trigger_id: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update trigger configuration synchronously."""
        return self._make_request("PUT", f"/triggers/{trigger_id}", data=trigger_data)

    async def delete_trigger_async(self, trigger_id: str) -> bool:
        """
        Delete workflow trigger asynchronously.

        Args:
            trigger_id: Unique trigger identifier

        Returns:
            True if deletion successful
        """
        await self._make_request_async("DELETE", f"/triggers/{trigger_id}")
        return True

    def delete_trigger(self, trigger_id: str) -> bool:
        """Delete workflow trigger synchronously."""
        self._make_request("DELETE", f"/triggers/{trigger_id}")
        return True

    # Workflow Templates APIs

    async def get_workflow_templates_async(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve workflow templates asynchronously.

        Args:
            category: Optional template category filter
            limit: Maximum number of templates to return
            offset: Number of templates to skip

        Returns:
            Dict containing workflow templates
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return await self._make_request_async("GET", "/templates/workflows", params=params)

    def get_workflow_templates(
        self,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieve workflow templates synchronously."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if category:
            params["category"] = category

        return self._make_request("GET", "/templates/workflows", params=params)

    async def create_workflow_from_template_async(self, template_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create workflow from template asynchronously.

        Args:
            template_id: Unique template identifier
            workflow_data: Workflow-specific configuration

        Returns:
            Dict containing created workflow data
        """
        payload = {
            "templateId": template_id,
            "workflowData": workflow_data
        }
        return await self._make_request_async("POST", "/workflows/from-template", data=payload)

    def create_workflow_from_template(self, template_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow from template synchronously."""
        payload = {
            "templateId": template_id,
            "workflowData": workflow_data
        }
        return self._make_request("POST", "/workflows/from-template", data=payload)
