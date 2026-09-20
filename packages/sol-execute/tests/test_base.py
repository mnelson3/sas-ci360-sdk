#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SAS CI360 Execute Module

Comprehensive test suite for the CI360ExecuteBase class and its APIs.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch

from sasci360solexecute.base import CI360ExecuteBase, CI360ExecuteConfig, CI360ExecuteError


class TestCI360ExecuteConfig(unittest.TestCase):
    """Test cases for CI360ExecuteConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CI360ExecuteConfig()
        self.assertEqual(config.algorithm, "HS256")
        self.assertEqual(config.api_base, "/marketingExecution")
        self.assertEqual(config.encoding, "utf-8")
        self.assertIsNone(config.host)
        self.assertIsNone(config.secret_key)
        self.assertIsNone(config.tenant_id)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_backoff, 0.5)
        self.assertTrue(config.enable_compression)
        self.assertEqual(config.max_concurrent_jobs, 10)
        self.assertEqual(config.job_timeout, 3600)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CI360ExecuteConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            timeout=60,
            max_concurrent_jobs=5
        )
        self.assertEqual(config.host, "https://api.example.com")
        self.assertEqual(config.secret_key, "test-secret")
        self.assertEqual(config.tenant_id, "test-tenant")
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.max_concurrent_jobs, 5)


class TestCI360ExecuteBase(unittest.TestCase):
    """Test cases for CI360ExecuteBase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360ExecuteConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_initialization_success(self, mock_encryption_class, mock_session_class):
        """Test successful initialization."""
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = CI360ExecuteBase(self.config)

        self.assertEqual(client.config, self.config)
        self.assertEqual(client.token, "test-token")

    def test_initialization_missing_config(self):
        with self.assertRaises(CI360ExecuteError):
            CI360ExecuteBase(CI360ExecuteConfig())

    def test_initialization_unsupported_algorithm(self):
        config = CI360ExecuteConfig(
            host="https://api.example.com", secret_key="s", tenant_id="t", algorithm="MD5"
        )
        with self.assertRaises(CI360ExecuteError):
            CI360ExecuteBase(config)

    def test_initialization_non_positive_batch_size(self):
        config = CI360ExecuteConfig(
            host="https://api.example.com", secret_key="s", tenant_id="t", batch_size=0
        )
        with self.assertRaises(CI360ExecuteError):
            CI360ExecuteBase(config)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption', None)
    def test_generate_token_raises_auth_error_when_encryption_unavailable(self, mock_session_class):
        from sasci360solexecute.base import CI360ExecuteAuthError
        with self.assertRaises(CI360ExecuteAuthError):
            CI360ExecuteBase(self.config)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_generate_token_wraps_any_failure_as_auth_error(self, mock_encryption_class, mock_session_class):
        from sasci360solexecute.base import CI360ExecuteAuthError
        mock_encryption_class.return_value.generate_jwt.side_effect = RuntimeError("bad key")

        with self.assertRaises(CI360ExecuteAuthError):
            CI360ExecuteBase(self.config)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_get_auth_headers(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-jwt-token"

        client = CI360ExecuteBase(self.config)
        headers = client.get_auth_headers()

        self.assertEqual(headers["Authorization"], "Bearer test-jwt-token")
        self.assertEqual(headers["X-Tenant-ID"], "test-tenant-id")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_validate_connection_async_true_on_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=200)

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertTrue(result)
        self.assertTrue(client._connected)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_validate_connection_async_false_on_non_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertFalse(result)
        self.assertFalse(client._connected)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_validate_connection_async_false_when_session_raises(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.side_effect = ConnectionError("refused")

        client = CI360ExecuteBase(self.config)

        self.assertFalse(asyncio.run(client.validate_connection_async()))

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_validate_connection_sync_delegates_to_async(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=200)

        client = CI360ExecuteBase(self.config)

        self.assertTrue(client.validate_connection())

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.asyncio.run')
    def test_validate_connection_sync_false_when_asyncio_run_raises(
        self, mock_asyncio_run, mock_encryption_class, mock_session_class
    ):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ExecuteBase(self.config)
        mock_asyncio_run.side_effect = RuntimeError("loop already running")

        self.assertFalse(client.validate_connection())

    def _connected_client(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ExecuteBase(self.config)
        client._connected = True
        return client, mock_session_class.return_value

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_returns_parsed_json_on_success(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/campaigns"))

        self.assertEqual(result, {"ok": True})

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_reconnects_when_not_connected(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ExecuteBase(self.config)
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)
        response = Mock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/campaigns"))

        self.assertEqual(result, {"ok": True})
        mock_session.get.assert_called_once()

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_raises_connection_error_when_reconnect_fails(
        self, mock_encryption_class, mock_session_class
    ):
        from sasci360solexecute.base import CI360ExecuteConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ExecuteBase(self.config)
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        with self.assertRaises(CI360ExecuteConnectionError):
            asyncio.run(client._make_request_async("GET", "/campaigns"))

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_401_raises_auth_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solexecute.base import CI360ExecuteAuthError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=401)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("401")
        mock_session.request.return_value = response

        with self.assertRaises(CI360ExecuteAuthError):
            asyncio.run(client._make_request_async("GET", "/campaigns"))

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_5xx_raises_connection_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solexecute.base import CI360ExecuteConnectionError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=503)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("503")
        mock_session.request.return_value = response

        with self.assertRaises(CI360ExecuteConnectionError):
            asyncio.run(client._make_request_async("GET", "/campaigns"))

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_other_4xx_raises_generic_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=404)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("404")
        mock_session.request.return_value = response

        with self.assertRaises(CI360ExecuteError):
            asyncio.run(client._make_request_async("GET", "/campaigns"))

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_network_error_raises_connection_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solexecute.base import CI360ExecuteConnectionError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        mock_session.request.side_effect = requests_module.exceptions.ConnectionError("refused")

        with self.assertRaises(CI360ExecuteConnectionError):
            asyncio.run(client._make_request_async("GET", "/campaigns"))

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_make_request_sync_logs_and_reraises(self, mock_request_async, mock_encryption_class, mock_session_class):
        from sasci360solexecute.base import CI360ExecuteConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ExecuteBase(self.config)
        mock_request_async.side_effect = CI360ExecuteConnectionError("down")

        with self.assertRaises(CI360ExecuteConnectionError):
            client._make_request("GET", "/campaigns")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_sync_context_manager_success(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        with CI360ExecuteBase(self.config) as client:
            self.assertTrue(client._connected)
        mock_session.close.assert_called_once()

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_sync_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        from sasci360solexecute.base import CI360ExecuteConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        with self.assertRaises(CI360ExecuteConnectionError):
            with CI360ExecuteBase(self.config):
                pass

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_async_context_manager_success(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        async def _run():
            async with CI360ExecuteBase(self.config) as client:
                return client._connected

        self.assertTrue(asyncio.run(_run()))
        mock_session.close.assert_called_once()

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_async_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        from sasci360solexecute.base import CI360ExecuteConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        async def _run():
            async with CI360ExecuteBase(self.config):
                pass

        with self.assertRaises(CI360ExecuteConnectionError):
            asyncio.run(_run())

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_execute_campaign_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async campaign execution."""
        mock_request.return_value = {"executionId": "exec-123", "status": "running"}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.execute_campaign_async("camp-123", {"priority": "high"}))

        self.assertEqual(result["executionId"], "exec-123")
        expected_payload = {"campaignId": "camp-123", "executionParams": {"priority": "high"}}
        mock_request.assert_called_once_with("POST", "/campaigns/execute", data=expected_payload)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_execution_status_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async execution status retrieval."""
        mock_request.return_value = {"executionId": "exec-123", "status": "completed", "progress": 100}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.get_execution_status_async("exec-123"))

        self.assertEqual(result["status"], "completed")
        mock_request.assert_called_once_with("GET", "/executions/exec-123")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_cancel_execution_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async execution cancellation."""
        mock_request.return_value = None

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.cancel_execution_async("exec-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("POST", "/executions/exec-123/cancel")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_submit_batch_job_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async batch job submission."""
        job_data = {
            "name": "Customer Update Batch",
            "operations": [{"type": "update", "data": {"customerId": "123"}}]
        }
        mock_request.return_value = {"jobId": "job-123", "status": "queued"}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.submit_batch_job_async(job_data))

        self.assertEqual(result["jobId"], "job-123")
        mock_request.assert_called_once_with("POST", "/batch/jobs", data=job_data)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_batch_job_status_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async batch job status retrieval."""
        mock_request.return_value = {"jobId": "job-123", "status": "running", "progress": 45}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.get_batch_job_status_async("job-123"))

        self.assertEqual(result["status"], "running")
        mock_request.assert_called_once_with("GET", "/batch/jobs/job-123")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_cancel_batch_job_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async batch job cancellation."""
        mock_request.return_value = None

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.cancel_batch_job_async("job-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("POST", "/batch/jobs/job-123/cancel")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_batch_jobs_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async batch jobs listing."""
        mock_request.return_value = {"jobs": [], "total": 0}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.get_batch_jobs_async(limit=25, offset=50, status_filter="completed"))

        self.assertEqual(result, {"jobs": [], "total": 0})
        expected_params = {"limit": 25, "offset": 50, "status": "completed"}
        mock_request.assert_called_once_with("GET", "/batch/jobs", params=expected_params)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_schedule_job_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async job scheduling."""
        schedule_data = {
            "name": "Daily Customer Sync",
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "jobType": "batch",
            "jobData": {"type": "sync"}
        }
        mock_request.return_value = {"scheduleId": "sched-123", "nextRun": "2025-12-14T02:00:00Z"}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.schedule_job_async(schedule_data))

        self.assertEqual(result["scheduleId"], "sched-123")
        mock_request.assert_called_once_with("POST", "/schedules", data=schedule_data)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_scheduled_jobs_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async scheduled jobs listing."""
        mock_request.return_value = {"schedules": [], "total": 0}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.get_scheduled_jobs_async(limit=10, offset=20, active_only=False))

        self.assertEqual(result, {"schedules": [], "total": 0})
        expected_params = {"limit": 10, "offset": 20, "activeOnly": False}
        mock_request.assert_called_once_with("GET", "/schedules", params=expected_params)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_update_schedule_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async schedule update."""
        update_data = {"schedule": "0 4 * * *"}  # Change to 4 AM
        mock_request.return_value = {"scheduleId": "sched-123", "schedule": "0 4 * * *"}

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.update_schedule_async("sched-123", update_data))

        self.assertEqual(result["schedule"], "0 4 * * *")
        mock_request.assert_called_once_with("PUT", "/schedules/sched-123", data=update_data)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_delete_schedule_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async schedule deletion."""
        mock_request.return_value = None

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.delete_schedule_async("sched-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/schedules/sched-123")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_execution_metrics_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async execution metrics retrieval."""
        mock_request.return_value = {
            "totalExecutions": 150,
            "successfulExecutions": 145,
            "failedExecutions": 5,
            "averageExecutionTime": 45.2
        }

        client = CI360ExecuteBase(self.config)
        result = asyncio.run(client.get_execution_metrics_async(
            start_date="2025-12-01",
            end_date="2025-12-13",
            campaign_id="camp-123"
        ))

        self.assertEqual(result["totalExecutions"], 150)
        expected_params = {
            "startDate": "2025-12-01",
            "endDate": "2025-12-13",
            "campaignId": "camp-123"
        }
        mock_request.assert_called_once_with("GET", "/metrics/executions", params=expected_params)

    # Synchronous method tests

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_execute_campaign_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous campaign execution."""
        mock_request.return_value = {"executionId": "exec-123", "status": "running"}

        client = CI360ExecuteBase(self.config)
        result = client.execute_campaign("camp-123")

        self.assertEqual(result["executionId"], "exec-123")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_execution_status_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous execution status retrieval."""
        mock_request.return_value = {"executionId": "exec-123", "status": "completed"}

        client = CI360ExecuteBase(self.config)
        result = client.get_execution_status("exec-123")

        self.assertEqual(result["status"], "completed")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_submit_batch_job_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous batch job submission."""
        job_data = {"name": "Test Batch Job"}
        mock_request.return_value = {"jobId": "job-123"}

        client = CI360ExecuteBase(self.config)
        result = client.submit_batch_job(job_data)

        self.assertEqual(result["jobId"], "job-123")

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_cancel_execution_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = None
        client = CI360ExecuteBase(self.config)

        self.assertTrue(client.cancel_execution("exec-123"))
        mock_request.assert_called_once_with("POST", "/executions/exec-123/cancel", None, None)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_batch_job_status_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"jobId": "job-123", "status": "running"}
        client = CI360ExecuteBase(self.config)

        result = client.get_batch_job_status("job-123")

        self.assertEqual(result["status"], "running")
        mock_request.assert_called_once_with("GET", "/batch/jobs/job-123", None, None)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_cancel_batch_job_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = None
        client = CI360ExecuteBase(self.config)

        self.assertTrue(client.cancel_batch_job("job-123"))
        mock_request.assert_called_once_with("POST", "/batch/jobs/job-123/cancel", None, None)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_batch_jobs_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"jobs": []}
        client = CI360ExecuteBase(self.config)

        client.get_batch_jobs(limit=25, offset=50, status_filter="completed")

        mock_request.assert_called_once_with(
            "GET", "/batch/jobs", None, {"limit": 25, "offset": 50, "status": "completed"}
        )

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_schedule_job_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"scheduleId": "sched-123"}
        client = CI360ExecuteBase(self.config)

        client.schedule_job({"name": "Daily Sync"})

        mock_request.assert_called_once_with("POST", "/schedules", {"name": "Daily Sync"}, None)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_scheduled_jobs_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"schedules": []}
        client = CI360ExecuteBase(self.config)

        client.get_scheduled_jobs(limit=10, offset=20, active_only=False)

        mock_request.assert_called_once_with(
            "GET", "/schedules", None, {"limit": 10, "offset": 20, "activeOnly": False}
        )

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_update_schedule_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"scheduleId": "sched-123"}
        client = CI360ExecuteBase(self.config)

        client.update_schedule("sched-123", {"schedule": "0 4 * * *"})

        mock_request.assert_called_once_with("PUT", "/schedules/sched-123", {"schedule": "0 4 * * *"}, None)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_delete_schedule_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = None
        client = CI360ExecuteBase(self.config)

        self.assertTrue(client.delete_schedule("sched-123"))
        mock_request.assert_called_once_with("DELETE", "/schedules/sched-123", None, None)

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_get_execution_metrics_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"totalExecutions": 150}
        client = CI360ExecuteBase(self.config)

        client.get_execution_metrics(start_date="2025-12-01", end_date="2025-12-13", campaign_id="camp-123")

        mock_request.assert_called_once_with(
            "GET", "/metrics/executions", None,
            {"startDate": "2025-12-01", "endDate": "2025-12-13", "campaignId": "camp-123"},
        )


class TestCI360ExecuteErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360ExecuteConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    @patch('sasci360solexecute.base.CI360ExecuteBase._make_request_async')
    def test_execution_error_handling(self, mock_request, mock_encryption_class, mock_session_class):
        """Test execution error handling."""
        from sasci360solexecute.base import CI360ExecuteConnectionError
        mock_request.side_effect = CI360ExecuteConnectionError("Execution failed")

        client = CI360ExecuteBase(self.config)

        with self.assertRaises(CI360ExecuteConnectionError):
            asyncio.run(client.execute_campaign_async("camp-123"))

    # URL construction test
    #
    # Every test above mocks _make_request_async itself, so none of them
    # ever exercise the URL it builds. That let a real bug through:
    # urljoin(host + api_base, endpoint) silently drops api_base, because
    # urljoin treats a base URL with no trailing slash as a document to
    # replace rather than a directory to extend under RFC 3986 relative
    # reference resolution (same bug already fixed in sol-planning,
    # sol-content-delivery, and sol-data). This test mocks one level
    # deeper (the session's own .request call) to pin down the actual
    # URL requested.

    @patch('sasci360solexecute.base.requests.Session')
    @patch('sasci360solexecute.base.Encryption')
    def test_make_request_async_includes_api_base_in_url(self, mock_encryption_class, mock_session_class):
        """_make_request_async must build a URL under config.api_base, not just config.host."""
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_response = Mock()
        mock_response.content = b'{"ok": true}'
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status.return_value = None
        mock_session_class.return_value.request.return_value = mock_response

        client = CI360ExecuteBase(self.config)
        client._connected = True

        asyncio.run(client._make_request_async("GET", "/campaigns"))

        called_url = mock_session_class.return_value.request.call_args.kwargs["url"]
        self.assertEqual(called_url, "https://api.example.com/marketingExecution/campaigns")


if __name__ == '__main__':
    unittest.main()
