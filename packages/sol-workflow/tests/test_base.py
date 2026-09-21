#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SAS CI360 Workflow Module

Comprehensive test suite for the CI360WorkflowBase class and its APIs.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch

from sasci360solworkflow.base import CI360WorkflowBase, CI360WorkflowConfig, CI360WorkflowError


class TestCI360WorkflowConfig(unittest.TestCase):
    """Test cases for CI360WorkflowConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CI360WorkflowConfig()
        self.assertEqual(config.algorithm, "HS256")
        self.assertEqual(config.api_base, "/marketingWorkflow")
        self.assertEqual(config.encoding, "utf-8")
        self.assertIsNone(config.host)
        self.assertIsNone(config.secret_key)
        self.assertIsNone(config.tenant_id)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_backoff, 0.5)
        self.assertTrue(config.enable_compression)
        self.assertEqual(config.max_concurrent_workflows, 50)
        self.assertEqual(config.workflow_timeout, 7200)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CI360WorkflowConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            timeout=60,
            max_concurrent_workflows=25
        )
        self.assertEqual(config.host, "https://api.example.com")
        self.assertEqual(config.secret_key, "test-secret")
        self.assertEqual(config.tenant_id, "test-tenant")
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.max_concurrent_workflows, 25)


class TestCI360WorkflowBase(unittest.TestCase):
    """Test cases for CI360WorkflowBase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360WorkflowConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_initialization_success(self, mock_encryption_class, mock_session_class):
        """Test successful initialization."""
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = CI360WorkflowBase(self.config)

        self.assertEqual(client.config, self.config)
        self.assertEqual(client.token, "test-token")
        mock_encryption_class.assert_called_once()
        mock_session_class.assert_called_once()

    def test_initialization_missing_config(self):
        with self.assertRaises(CI360WorkflowError):
            CI360WorkflowBase(CI360WorkflowConfig())

    def test_initialization_unsupported_algorithm(self):
        config = CI360WorkflowConfig(
            host="https://api.example.com", secret_key="s", tenant_id="t", algorithm="MD5"
        )
        with self.assertRaises(CI360WorkflowError):
            CI360WorkflowBase(config)

    def test_initialization_non_positive_max_concurrent_workflows(self):
        config = CI360WorkflowConfig(
            host="https://api.example.com", secret_key="s", tenant_id="t", max_concurrent_workflows=0
        )
        with self.assertRaises(CI360WorkflowError):
            CI360WorkflowBase(config)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption', None)
    def test_generate_token_raises_auth_error_when_encryption_unavailable(self, mock_session_class):
        from sasci360solworkflow.base import CI360WorkflowAuthError
        with self.assertRaises(CI360WorkflowAuthError):
            CI360WorkflowBase(self.config)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_generate_token_wraps_any_failure_as_auth_error(self, mock_encryption_class, mock_session_class):
        from sasci360solworkflow.base import CI360WorkflowAuthError
        mock_encryption_class.return_value.generate_jwt.side_effect = RuntimeError("bad key")

        with self.assertRaises(CI360WorkflowAuthError):
            CI360WorkflowBase(self.config)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_get_auth_headers(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-jwt-token"

        client = CI360WorkflowBase(self.config)
        headers = client.get_auth_headers()

        self.assertEqual(headers["Authorization"], "Bearer test-jwt-token")
        self.assertEqual(headers["X-Tenant-ID"], "test-tenant-id")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_true_on_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=200)

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertTrue(result)
        self.assertTrue(client._connected)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_false_on_non_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertFalse(result)
        self.assertFalse(client._connected)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_false_when_session_raises(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.side_effect = ConnectionError("refused")

        client = CI360WorkflowBase(self.config)

        self.assertFalse(asyncio.run(client.validate_connection_async()))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_sync_delegates_to_async(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=200)

        client = CI360WorkflowBase(self.config)

        self.assertTrue(client.validate_connection())

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360apicore.rest_client.asyncio.run')
    def test_validate_connection_sync_false_when_asyncio_run_raises(
        self, mock_asyncio_run, mock_encryption_class, mock_session_class
    ):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360WorkflowBase(self.config)
        mock_asyncio_run.side_effect = RuntimeError("loop already running")

        self.assertFalse(client.validate_connection())

    def _connected_client(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360WorkflowBase(self.config)
        client._connected = True
        return client, mock_session_class.return_value

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_returns_parsed_json_on_success(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/workflows"))

        self.assertEqual(result, {"ok": True})

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_reconnects_when_not_connected(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360WorkflowBase(self.config)
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)
        response = Mock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/workflows"))

        self.assertEqual(result, {"ok": True})
        mock_session.get.assert_called_once()

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_raises_connection_error_when_reconnect_fails(
        self, mock_encryption_class, mock_session_class
    ):
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360WorkflowBase(self.config)
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        with self.assertRaises(CI360WorkflowConnectionError):
            asyncio.run(client._make_request_async("GET", "/workflows"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_401_raises_auth_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solworkflow.base import CI360WorkflowAuthError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=401)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("401")
        mock_session.request.return_value = response

        with self.assertRaises(CI360WorkflowAuthError):
            asyncio.run(client._make_request_async("GET", "/workflows"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_5xx_raises_connection_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=503)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("503")
        mock_session.request.return_value = response

        with self.assertRaises(CI360WorkflowConnectionError):
            asyncio.run(client._make_request_async("GET", "/workflows"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_other_4xx_raises_generic_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=404)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("404")
        mock_session.request.return_value = response

        with self.assertRaises(CI360WorkflowError):
            asyncio.run(client._make_request_async("GET", "/workflows"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_network_error_raises_connection_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        mock_session.request.side_effect = requests_module.exceptions.ConnectionError("refused")

        with self.assertRaises(CI360WorkflowConnectionError):
            asyncio.run(client._make_request_async("GET", "/workflows"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_make_request_sync_logs_and_reraises(self, mock_request_async, mock_encryption_class, mock_session_class):
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360WorkflowBase(self.config)
        mock_request_async.side_effect = CI360WorkflowConnectionError("down")

        with self.assertRaises(CI360WorkflowConnectionError):
            client._make_request("GET", "/workflows")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_sync_context_manager_success(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        with CI360WorkflowBase(self.config) as client:
            self.assertTrue(client._connected)
        mock_session.close.assert_called_once()

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_sync_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        with self.assertRaises(CI360WorkflowConnectionError):
            with CI360WorkflowBase(self.config):
                pass

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_async_context_manager_success(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        async def _run():
            async with CI360WorkflowBase(self.config) as client:
                return client._connected

        self.assertTrue(asyncio.run(_run()))
        mock_session.close.assert_called_once()

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_async_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        async def _run():
            async with CI360WorkflowBase(self.config):
                pass

        with self.assertRaises(CI360WorkflowConnectionError):
            asyncio.run(_run())

    # Workflow Management Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflows_async(self, mock_request, mock_session_class):
        """Test async workflow retrieval."""
        mock_request.return_value = {"workflows": [], "total": 0}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.get_workflows_async(limit=20, offset=40))

        self.assertEqual(result, {"workflows": [], "total": 0})
        mock_request.assert_called_once_with(
            "GET", "/workflows",
            params={"limit": 20, "offset": 40}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflow_async(self, mock_request, mock_session_class):
        """Test async single workflow retrieval."""
        workflow_data = {
            "id": "wf-123",
            "name": "Customer Onboarding Flow",
            "status": "active",
            "steps": ["welcome", "profile", "activation"]
        }
        mock_request.return_value = workflow_data

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.get_workflow_async("wf-123"))

        self.assertEqual(result["name"], "Customer Onboarding Flow")
        mock_request.assert_called_once_with("GET", "/workflows/wf-123")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_create_workflow_async(self, mock_request, mock_session_class):
        """Test async workflow creation."""
        workflow_data = {
            "name": "New Customer Workflow",
            "description": "Automated customer onboarding",
            "steps": [
                {"name": "send_welcome", "type": "email", "config": {"templateId": "welcome-1"}},
                {"name": "wait_24h", "type": "delay", "config": {"hours": 24}},
                {"name": "send_followup", "type": "email", "config": {"templateId": "followup-1"}}
            ]
        }
        mock_request.return_value = {"id": "wf-456", **workflow_data}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.create_workflow_async(workflow_data))

        self.assertEqual(result["id"], "wf-456")
        mock_request.assert_called_once_with("POST", "/workflows", data=workflow_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_update_workflow_async(self, mock_request, mock_session_class):
        """Test async workflow update."""
        update_data = {"name": "Updated Workflow Name", "status": "inactive"}
        mock_request.return_value = {"id": "wf-123", **update_data}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.update_workflow_async("wf-123", update_data))

        self.assertEqual(result["name"], "Updated Workflow Name")
        mock_request.assert_called_once_with("PUT", "/workflows/wf-123", data=update_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_delete_workflow_async(self, mock_request, mock_session_class):
        """Test async workflow deletion."""
        mock_request.return_value = None

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.delete_workflow_async("wf-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/workflows/wf-123")

    # Process Execution Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_start_process_async(self, mock_request, mock_session_class):
        """Test async process start."""
        input_data = {"customerId": "cust-123", "email": "customer@example.com"}
        mock_request.return_value = {
            "processId": "proc-789",
            "workflowId": "wf-123",
            "status": "running",
            "startedAt": "2025-12-13T10:00:00Z"
        }

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.start_process_async("wf-123", input_data))

        self.assertEqual(result["processId"], "proc-789")
        expected_payload = {"workflowId": "wf-123", "inputData": input_data}
        mock_request.assert_called_once_with("POST", "/processes/start", data=expected_payload)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_process_status_async(self, mock_request, mock_session_class):
        """Test async process status retrieval."""
        mock_request.return_value = {
            "processId": "proc-789",
            "status": "completed",
            "currentStep": "send_followup",
            "progress": 100,
            "outputData": {"emailSent": True}
        }

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.get_process_status_async("proc-789"))

        self.assertEqual(result["status"], "completed")
        mock_request.assert_called_once_with("GET", "/processes/proc-789")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_cancel_process_async(self, mock_request, mock_session_class):
        """Test async process cancellation."""
        mock_request.return_value = None

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.cancel_process_async("proc-789"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("POST", "/processes/proc-789/cancel")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_processes_async(self, mock_request, mock_session_class):
        """Test async process listing."""
        mock_request.return_value = {"processes": [], "total": 0}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.get_processes_async(limit=30, offset=60, status_filter="running"))

        self.assertEqual(result, {"processes": [], "total": 0})
        expected_params = {"limit": 30, "offset": 60, "status": "running"}
        mock_request.assert_called_once_with("GET", "/processes", params=expected_params)

    # Trigger Management Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_triggers_async(self, mock_request, mock_session_class):
        """Test async trigger retrieval."""
        mock_request.return_value = {"triggers": [], "total": 0}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.get_triggers_async(limit=25, offset=50))

        self.assertEqual(result, {"triggers": [], "total": 0})
        mock_request.assert_called_once_with(
            "GET", "/triggers",
            params={"limit": 25, "offset": 50}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_create_trigger_async(self, mock_request, mock_session_class):
        """Test async trigger creation."""
        trigger_data = {
            "name": "New Customer Trigger",
            "event": "customer.created",
            "workflowId": "wf-123",
            "conditions": {"source": "website"}
        }
        mock_request.return_value = {"id": "trig-999", **trigger_data}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.create_trigger_async(trigger_data))

        self.assertEqual(result["name"], "New Customer Trigger")
        mock_request.assert_called_once_with("POST", "/triggers", data=trigger_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_delete_trigger_async(self, mock_request, mock_session_class):
        """Test async trigger deletion."""
        mock_request.return_value = None

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.delete_trigger_async("trig-999"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/triggers/trig-999")

    # Template Management Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflow_templates_async(self, mock_request, mock_session_class):
        """Test async workflow template retrieval."""
        mock_request.return_value = {"templates": [], "total": 0}

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.get_workflow_templates_async(category="onboarding", limit=10))

        self.assertEqual(result, {"templates": [], "total": 0})
        expected_params = {"category": "onboarding", "limit": 10, "offset": 0}
        mock_request.assert_called_once_with("GET", "/templates/workflows", params=expected_params)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_create_workflow_from_template_async(self, mock_request, mock_session_class):
        """Test async workflow creation from template."""
        workflow_data = {"name": "My Custom Workflow", "customizations": {"emailTemplate": "custom-1"}}
        mock_request.return_value = {
            "id": "wf-888",
            "name": "My Custom Workflow",
            "templateId": "tmpl-777",
            "status": "draft"
        }

        client = CI360WorkflowBase(self.config)
        result = asyncio.run(client.create_workflow_from_template_async("tmpl-777", workflow_data))

        self.assertEqual(result["id"], "wf-888")
        expected_payload = {"templateId": "tmpl-777", "workflowData": workflow_data}
        mock_request.assert_called_once_with("POST", "/workflows/from-template", data=expected_payload)

    # Synchronous method tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflows_sync(self, mock_request, mock_session_class):
        """Test synchronous workflow retrieval."""
        mock_request.return_value = {"workflows": [], "total": 0}

        client = CI360WorkflowBase(self.config)
        result = client.get_workflows(limit=20)

        self.assertEqual(result["total"], 0)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_create_workflow_sync(self, mock_request, mock_session_class):
        """Test synchronous workflow creation."""
        workflow_data = {"name": "Test Workflow"}
        mock_request.return_value = {"id": "wf-123", **workflow_data}

        client = CI360WorkflowBase(self.config)
        result = client.create_workflow(workflow_data)

        self.assertEqual(result["id"], "wf-123")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_start_process_sync(self, mock_request, mock_session_class):
        """Test synchronous process start."""
        mock_request.return_value = {"processId": "proc-123", "status": "running"}

        client = CI360WorkflowBase(self.config)
        result = client.start_process("wf-123")

        self.assertEqual(result["processId"], "proc-123")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflows_sync_merges_filters(self, mock_request, mock_session_class):
        mock_request.return_value = {"workflows": []}
        client = CI360WorkflowBase(self.config)

        client.get_workflows(limit=20, offset=40, filters={"status": "active"})

        mock_request.assert_called_once_with(
            "GET", "/workflows", None, {"limit": 20, "offset": 40, "status": "active"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflows_async_merges_filters(self, mock_request, mock_session_class):
        mock_request.return_value = {"workflows": []}
        client = CI360WorkflowBase(self.config)

        asyncio.run(client.get_workflows_async(filters={"status": "active"}))

        mock_request.assert_called_once_with(
            "GET", "/workflows", params={"limit": 50, "offset": 0, "status": "active"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflow_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"id": "wf-1"}
        client = CI360WorkflowBase(self.config)

        client.get_workflow("wf-1")

        mock_request.assert_called_once_with("GET", "/workflows/wf-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_update_workflow_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"id": "wf-1", "name": "Renamed"}
        client = CI360WorkflowBase(self.config)

        client.update_workflow("wf-1", {"name": "Renamed"})

        mock_request.assert_called_once_with("PUT", "/workflows/wf-1", {"name": "Renamed"}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_delete_workflow_sync(self, mock_request, mock_session_class):
        mock_request.return_value = None
        client = CI360WorkflowBase(self.config)

        self.assertTrue(client.delete_workflow("wf-1"))
        mock_request.assert_called_once_with("DELETE", "/workflows/wf-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_process_status_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"status": "completed"}
        client = CI360WorkflowBase(self.config)

        result = client.get_process_status("proc-1")

        self.assertEqual(result["status"], "completed")
        mock_request.assert_called_once_with("GET", "/processes/proc-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_cancel_process_sync(self, mock_request, mock_session_class):
        mock_request.return_value = None
        client = CI360WorkflowBase(self.config)

        self.assertTrue(client.cancel_process("proc-1"))
        mock_request.assert_called_once_with("POST", "/processes/proc-1/cancel", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_processes_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"processes": []}
        client = CI360WorkflowBase(self.config)

        client.get_processes(limit=30, offset=60, status_filter="running")

        mock_request.assert_called_once_with(
            "GET", "/processes", None, {"limit": 30, "offset": 60, "status": "running"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_triggers_sync_merges_filters(self, mock_request, mock_session_class):
        mock_request.return_value = {"triggers": []}
        client = CI360WorkflowBase(self.config)

        client.get_triggers(limit=25, offset=50, filters={"event": "customer.created"})

        mock_request.assert_called_once_with(
            "GET", "/triggers", None, {"limit": 25, "offset": 50, "event": "customer.created"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_triggers_async_merges_filters(self, mock_request, mock_session_class):
        mock_request.return_value = {"triggers": []}
        client = CI360WorkflowBase(self.config)

        asyncio.run(client.get_triggers_async(filters={"event": "customer.created"}))

        mock_request.assert_called_once_with(
            "GET", "/triggers", params={"limit": 50, "offset": 0, "event": "customer.created"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_create_trigger_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"id": "trig-1"}
        client = CI360WorkflowBase(self.config)

        client.create_trigger({"name": "New Trigger"})

        mock_request.assert_called_once_with("POST", "/triggers", {"name": "New Trigger"}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_update_trigger_async_and_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"id": "trig-1"}
        client = CI360WorkflowBase(self.config)

        asyncio.run(client.update_trigger_async("trig-1", {"name": "Renamed"}))
        mock_request.assert_called_with("PUT", "/triggers/trig-1", data={"name": "Renamed"})

        client.update_trigger("trig-1", {"name": "Renamed"})
        mock_request.assert_called_with("PUT", "/triggers/trig-1", {"name": "Renamed"}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_delete_trigger_sync(self, mock_request, mock_session_class):
        mock_request.return_value = None
        client = CI360WorkflowBase(self.config)

        self.assertTrue(client.delete_trigger("trig-1"))
        mock_request.assert_called_once_with("DELETE", "/triggers/trig-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_get_workflow_templates_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"templates": []}
        client = CI360WorkflowBase(self.config)

        client.get_workflow_templates(category="onboarding", limit=10)

        mock_request.assert_called_once_with(
            "GET", "/templates/workflows", None, {"limit": 10, "offset": 0, "category": "onboarding"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_create_workflow_from_template_sync(self, mock_request, mock_session_class):
        mock_request.return_value = {"id": "wf-1"}
        client = CI360WorkflowBase(self.config)

        client.create_workflow_from_template("tmpl-1", {"name": "Custom"})

        mock_request.assert_called_once_with(
            "POST", "/workflows/from-template", {"templateId": "tmpl-1", "workflowData": {"name": "Custom"}}, None
        )


class TestCI360WorkflowErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360WorkflowConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360solworkflow.base.CI360WorkflowBase._make_request_async')
    def test_connection_error_handling(self, mock_request, mock_session_class):
        """Test connection error handling."""
        from sasci360solworkflow.base import CI360WorkflowConnectionError
        mock_request.side_effect = CI360WorkflowConnectionError("Workflow service unavailable")

        client = CI360WorkflowBase(self.config)

        with self.assertRaises(CI360WorkflowConnectionError):
            asyncio.run(client.get_workflows_async())

    # URL construction test
    #
    # Every test above mocks _make_request_async itself, so none of them
    # ever exercise the URL it builds. That let a real bug through:
    # urljoin(host + api_base, endpoint) silently drops api_base, because
    # urljoin treats a base URL with no trailing slash as a document to
    # replace rather than a directory to extend under RFC 3986 relative
    # reference resolution (same bug already fixed in sol-planning,
    # sol-content-delivery, sol-data, and sol-execute). This test mocks
    # one level deeper (the session's own .request call) to pin down the
    # actual URL requested.

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_includes_api_base_in_url(self, mock_encryption_class, mock_session_class):
        """_make_request_async must build a URL under config.api_base, not just config.host."""
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_response = Mock()
        mock_response.content = b'{"ok": true}'
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status.return_value = None
        mock_session_class.return_value.request.return_value = mock_response

        client = CI360WorkflowBase(self.config)
        client._connected = True

        asyncio.run(client._make_request_async("GET", "/workflows"))

        called_url = mock_session_class.return_value.request.call_args.kwargs["url"]
        self.assertEqual(called_url, "https://api.example.com/marketingWorkflow/workflows")


if __name__ == '__main__':
    unittest.main()
