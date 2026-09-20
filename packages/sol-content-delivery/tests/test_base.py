#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SAS CI360 Content Delivery Module

Comprehensive test suite for the CI360ContentDeliveryBase class and its APIs.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch

import requests

from sasci360solcontentdelivery.base import (
    CI360ContentDeliveryAuthError,
    CI360ContentDeliveryBase,
    CI360ContentDeliveryConfig,
    CI360ContentDeliveryConnectionError,
    CI360ContentDeliveryError,
    CI360ContentDeliveryValidationError,
)


class TestCI360ContentDeliveryConfig(unittest.TestCase):
    """Test cases for CI360ContentDeliveryConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CI360ContentDeliveryConfig()
        self.assertEqual(config.algorithm, "HS256")
        self.assertEqual(config.api_base, "/digital-assets")
        self.assertEqual(config.encoding, "utf-8")
        self.assertIsNone(config.host)
        self.assertIsNone(config.secret_key)
        self.assertIsNone(config.tenant_id)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_backoff, 0.5)
        self.assertTrue(config.enable_compression)
        self.assertEqual(config.max_file_size_mb, 100)
        self.assertEqual(len(config.supported_formats), 9)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            timeout=60,
            max_file_size_mb=50
        )
        self.assertEqual(config.host, "https://api.example.com")
        self.assertEqual(config.secret_key, "test-secret")
        self.assertEqual(config.tenant_id, "test-tenant")
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.max_file_size_mb, 50)


class TestCI360ContentDeliveryBase(unittest.TestCase):
    """Test cases for CI360ContentDeliveryBase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_initialization_success(self, mock_request, mock_encryption_class, mock_session_class):
        """Test successful initialization."""
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = CI360ContentDeliveryBase(self.config)

        self.assertEqual(client.config, self.config)
        self.assertEqual(client.token, "test-token")

    # Digital Asset Management Tests

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_assets_async_merges_filters_into_params(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"assets": [], "total": 0}

        client = CI360ContentDeliveryBase(self.config)
        asyncio.run(client.get_assets_async(limit=30, offset=60, filters={"format": "jpg"}))

        mock_request.assert_called_once_with(
            "GET", "/assets", params={"limit": 30, "offset": 60, "format": "jpg"}
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_assets_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async asset retrieval."""
        mock_request.return_value = {"assets": [], "total": 0}

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.get_assets_async(limit=30, offset=60))

        self.assertEqual(result, {"assets": [], "total": 0})
        mock_request.assert_called_once_with(
            "GET", "/assets",
            params={"limit": 30, "offset": 60}
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_asset_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async single asset retrieval."""
        asset_data = {
            "id": "asset-123",
            "name": "Holiday Banner 2025",
            "type": "image",
            "format": "jpg",
            "size": 245760,
            "url": "https://cdn.example.com/assets/asset-123.jpg"
        }
        mock_request.return_value = asset_data

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.get_asset_async("asset-123"))

        self.assertEqual(result["name"], "Holiday Banner 2025")
        mock_request.assert_called_once_with("GET", "/assets/asset-123")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_update_asset_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async asset update."""
        update_data = {"name": "Updated Banner Name", "tags": ["holiday", "2025", "promo"]}
        mock_request.return_value = {"id": "asset-123", **update_data}

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.update_asset_async("asset-123", update_data))

        self.assertEqual(result["name"], "Updated Banner Name")
        mock_request.assert_called_once_with("PUT", "/assets/asset-123", data=update_data)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_delete_asset_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async asset deletion."""
        mock_request.return_value = None

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.delete_asset_async("asset-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/assets/asset-123")

    # Content Delivery Tests

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_deliver_content_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async content delivery."""
        delivery_config = {
            "channels": ["email", "sms"],
            "recipients": ["user-123", "user-456"],
            "schedule": "2025-12-15T09:00:00Z"
        }
        mock_request.return_value = {
            "deliveryId": "del-789",
            "assetId": "asset-123",
            "status": "scheduled",
            "scheduledFor": "2025-12-15T09:00:00Z"
        }

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.deliver_content_async("asset-123", delivery_config))

        self.assertEqual(result["deliveryId"], "del-789")
        expected_payload = {"assetId": "asset-123", "deliveryConfig": delivery_config}
        mock_request.assert_called_once_with("POST", "/delivery/send", data=expected_payload)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_delivery_status_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async delivery status retrieval."""
        mock_request.return_value = {
            "deliveryId": "del-789",
            "status": "completed",
            "deliveredTo": 150,
            "failed": 5,
            "completionRate": 0.967
        }

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.get_delivery_status_async("del-789"))

        self.assertEqual(result["status"], "completed")
        mock_request.assert_called_once_with("GET", "/delivery/del-789")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_deliveries_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async delivery listing."""
        mock_request.return_value = {"deliveries": [], "total": 0}

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.get_deliveries_async(limit=25, offset=50, status_filter="completed"))

        self.assertEqual(result, {"deliveries": [], "total": 0})
        expected_params = {"limit": 25, "offset": 50, "status": "completed"}
        mock_request.assert_called_once_with("GET", "/delivery", params=expected_params)

    # Content Template Tests

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_content_templates_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async content template retrieval."""
        mock_request.return_value = {"templates": [], "total": 0}

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.get_content_templates_async(category="email", limit=15))

        self.assertEqual(result, {"templates": [], "total": 0})
        expected_params = {"category": "email", "limit": 15, "offset": 0}
        mock_request.assert_called_once_with("GET", "/templates/content", params=expected_params)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_create_content_from_template_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async content creation from template."""
        content_data = {
            "name": "Holiday Newsletter",
            "variables": {"subject": "Happy Holidays 2025!", "sender": "marketing@company.com"}
        }
        mock_request.return_value = {
            "id": "content-999",
            "name": "Holiday Newsletter",
            "templateId": "tmpl-888",
            "status": "ready"
        }

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.create_content_from_template_async("tmpl-888", content_data))

        self.assertEqual(result["id"], "content-999")
        expected_payload = {"templateId": "tmpl-888", "contentData": content_data}
        mock_request.assert_called_once_with("POST", "/content/from-template", data=expected_payload)

    # Content Analytics Tests

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_content_analytics_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async content analytics retrieval."""
        mock_request.return_value = {
            "assetId": "asset-123",
            "totalViews": 5000,
            "uniqueViews": 3200,
            "clicks": 450,
            "shares": 25,
            "engagementRate": 0.141
        }

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.get_content_analytics_async(
            asset_id="asset-123",
            start_date="2025-12-01",
            end_date="2025-12-13"
        ))

        self.assertEqual(result["totalViews"], 5000)
        expected_params = {
            "assetId": "asset-123",
            "startDate": "2025-12-01",
            "endDate": "2025-12-13"
        }
        mock_request.assert_called_once_with("GET", "/analytics/content", params=expected_params)

    # Synchronous method tests

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_assets_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous asset retrieval."""
        mock_request.return_value = {"assets": [], "total": 0}

        client = CI360ContentDeliveryBase(self.config)
        result = client.get_assets(limit=30)

        self.assertEqual(result["total"], 0)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_update_asset_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous asset update."""
        update_data = {"name": "Updated Asset"}
        mock_request.return_value = {"id": "asset-123", **update_data}

        client = CI360ContentDeliveryBase(self.config)
        result = client.update_asset("asset-123", update_data)

        self.assertEqual(result["name"], "Updated Asset")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_deliver_content_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous content delivery."""
        delivery_config = {"channels": ["email"]}
        mock_request.return_value = {"deliveryId": "del-123", "status": "sent"}

        client = CI360ContentDeliveryBase(self.config)
        result = client.deliver_content("asset-123", delivery_config)

        self.assertEqual(result["deliveryId"], "del-123")


class TestCI360ContentDeliveryErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_validation_error_handling(self, mock_request, mock_encryption_class, mock_session_class):
        """Test validation error handling."""
        from sasci360solcontentdelivery.base import CI360ContentDeliveryValidationError
        mock_request.side_effect = CI360ContentDeliveryValidationError("Invalid file format")

        client = CI360ContentDeliveryBase(self.config)

        with self.assertRaises(CI360ContentDeliveryValidationError):
            asyncio.run(client.get_assets_async())


class TestCI360ContentDeliveryConfigValidation(unittest.TestCase):
    """Test cases for _validate_config's error branches - none of these
    need Session/Encryption mocked since validation runs before either
    is created."""

    def test_missing_required_fields_raises(self):
        with self.assertRaises(CI360ContentDeliveryValidationError) as ctx:
            CI360ContentDeliveryBase(CI360ContentDeliveryConfig())
        self.assertIn("host", str(ctx.exception))
        self.assertIn("secret_key", str(ctx.exception))
        self.assertIn("tenant_id", str(ctx.exception))

    def test_unsupported_algorithm_raises(self):
        config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="s",
            tenant_id="t",
            algorithm="MD5",
        )
        with self.assertRaises(CI360ContentDeliveryValidationError) as ctx:
            CI360ContentDeliveryBase(config)
        self.assertIn("MD5", str(ctx.exception))

    def test_non_positive_max_file_size_raises(self):
        config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="s",
            tenant_id="t",
            max_file_size_mb=0,
        )
        with self.assertRaises(CI360ContentDeliveryValidationError):
            CI360ContentDeliveryBase(config)


class TestCI360ContentDeliveryAuth(unittest.TestCase):
    """get_auth_headers and _generate_token's error wrapping."""

    def setUp(self):
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_get_auth_headers_includes_bearer_token_and_tenant(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"

        client = CI360ContentDeliveryBase(self.config)
        headers = client.get_auth_headers()

        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["X-Tenant-ID"], "test-tenant-id")
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_generate_token_wraps_any_failure_as_auth_error(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.side_effect = RuntimeError("bad key")

        with self.assertRaises(CI360ContentDeliveryAuthError) as ctx:
            CI360ContentDeliveryBase(self.config)
        self.assertIn("bad key", str(ctx.exception))


class TestCI360ContentDeliveryConnectionValidation(unittest.TestCase):
    """validate_connection_async/validate_connection, mocked at the
    session.get boundary (not at _make_request_async, which every other
    test in this file mocks out - these are what actually exercise the
    logic that boundary hides)."""

    def setUp(self):
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_validate_connection_async_true_on_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertTrue(result)
        self.assertTrue(client._connected)
        called_kwargs = mock_session.get.call_args.kwargs
        self.assertEqual(called_kwargs["timeout"], self.config.timeout)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_validate_connection_async_false_on_non_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertFalse(result)
        self.assertFalse(client._connected)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_validate_connection_async_false_when_session_raises(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.side_effect = requests.exceptions.ConnectionError("refused")

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertFalse(result)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_validate_connection_sync_delegates_to_async(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=200)

        client = CI360ContentDeliveryBase(self.config)

        self.assertTrue(client.validate_connection())

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.asyncio.run')
    def test_validate_connection_sync_false_when_asyncio_run_raises(
        self, mock_asyncio_run, mock_encryption_class, mock_session_class
    ):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ContentDeliveryBase(self.config)
        mock_asyncio_run.side_effect = RuntimeError("loop already running")

        self.assertFalse(client.validate_connection())


class TestCI360ContentDeliveryMakeRequest(unittest.TestCase):
    """_make_request_async and _make_request, mocked at the session
    boundary - the actual connection-check, retry-relevant plumbing, and
    HTTP-status-to-exception mapping that every other test in this file
    bypasses by mocking _make_request_async itself."""

    def setUp(self):
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    def _connected_client(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ContentDeliveryBase(self.config)
        client._connected = True  # bypass the auto-reconnect path for these tests
        return client, mock_session_class.return_value

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_returns_parsed_json_on_success(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/assets"))

        self.assertEqual(result, {"ok": True})
        called_kwargs = mock_session.request.call_args.kwargs
        self.assertEqual(called_kwargs["method"], "GET")
        # Regression: urljoin(host + api_base, endpoint) silently drops api_base
        # when host has no trailing slash (same bug class fixed in sol-planning).
        self.assertEqual(called_kwargs["url"], "https://api.example.com/digital-assets/assets")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_returns_empty_dict_when_no_content(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        mock_session.request.return_value = Mock(content=b"")

        result = asyncio.run(client._make_request_async("DELETE", "/assets/1"))

        self.assertEqual(result, {})

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_reconnects_when_not_connected(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ContentDeliveryBase(self.config)  # _connected starts False
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)  # health check succeeds
        response = Mock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/assets"))

        self.assertEqual(result, {"ok": True})
        mock_session.get.assert_called_once()  # the reconnect health check happened

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_raises_connection_error_when_reconnect_fails(
        self, mock_encryption_class, mock_session_class
    ):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ContentDeliveryBase(self.config)
        mock_session_class.return_value.get.return_value = Mock(status_code=503)  # health check fails

        with self.assertRaises(CI360ContentDeliveryConnectionError):
            asyncio.run(client._make_request_async("GET", "/assets"))

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_401_raises_auth_error(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=401)
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("401")
        mock_session.request.return_value = response

        with self.assertRaises(CI360ContentDeliveryAuthError):
            asyncio.run(client._make_request_async("GET", "/assets"))

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_5xx_raises_connection_error(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=503)
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("503")
        mock_session.request.return_value = response

        with self.assertRaises(CI360ContentDeliveryConnectionError):
            asyncio.run(client._make_request_async("GET", "/assets"))

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_other_4xx_raises_generic_error(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = Mock(status_code=404)
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        mock_session.request.return_value = response

        with self.assertRaises(CI360ContentDeliveryError):
            asyncio.run(client._make_request_async("GET", "/assets"))

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_make_request_async_network_error_raises_connection_error(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        mock_session.request.side_effect = requests.exceptions.ConnectionError("refused")

        with self.assertRaises(CI360ContentDeliveryConnectionError):
            asyncio.run(client._make_request_async("GET", "/assets"))

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_make_request_sync_logs_and_reraises(self, mock_request_async, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360ContentDeliveryBase(self.config)
        mock_request_async.side_effect = CI360ContentDeliveryConnectionError("down")

        with self.assertRaises(CI360ContentDeliveryConnectionError):
            client._make_request("GET", "/assets")


class TestCI360ContentDeliverySyncWrappers(unittest.TestCase):
    """The sync wrapper methods that only get exercised through their
    _async counterpart elsewhere in this file, or not at all."""

    def setUp(self):
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_assets_sync_merges_filters_into_params(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"assets": [], "total": 0}
        client = CI360ContentDeliveryBase(self.config)

        client.get_assets(limit=30, offset=60, filters={"format": "jpg"})

        mock_request.assert_called_once_with(
            "GET", "/assets", None, {"limit": 30, "offset": 60, "format": "jpg"}
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_asset_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "asset-1"}
        client = CI360ContentDeliveryBase(self.config)

        result = client.get_asset("asset-1")

        self.assertEqual(result["id"], "asset-1")
        mock_request.assert_called_once_with("GET", "/assets/asset-1", None, None)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_delete_asset_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = None
        client = CI360ContentDeliveryBase(self.config)

        self.assertTrue(client.delete_asset("asset-1"))
        mock_request.assert_called_once_with("DELETE", "/assets/asset-1", None, None)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_deliveries_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"deliveries": []}
        client = CI360ContentDeliveryBase(self.config)

        result = client.get_deliveries(status_filter="failed")

        self.assertEqual(result, {"deliveries": []})
        mock_request.assert_called_once_with(
            "GET", "/delivery", None, {"limit": 50, "offset": 0, "status": "failed"}
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_delivery_status_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"status": "sent"}
        client = CI360ContentDeliveryBase(self.config)

        result = client.get_delivery_status("del-1")

        self.assertEqual(result["status"], "sent")
        mock_request.assert_called_once_with("GET", "/delivery/del-1", None, None)

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_content_templates_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"templates": []}
        client = CI360ContentDeliveryBase(self.config)

        result = client.get_content_templates(category="email")

        self.assertEqual(result, {"templates": []})
        mock_request.assert_called_once_with(
            "GET", "/templates/content", None, {"limit": 50, "offset": 0, "category": "email"}
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_create_content_from_template_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "content-1"}
        client = CI360ContentDeliveryBase(self.config)

        result = client.create_content_from_template("tmpl-1", {"subject": "Hi"})

        self.assertEqual(result["id"], "content-1")
        mock_request.assert_called_once_with(
            "POST", "/content/from-template",
            {"templateId": "tmpl-1", "contentData": {"subject": "Hi"}}, None,
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    @patch('sasci360solcontentdelivery.base.CI360ContentDeliveryBase._make_request_async')
    def test_get_content_analytics_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"totalViews": 10}
        client = CI360ContentDeliveryBase(self.config)

        result = client.get_content_analytics(asset_id="asset-1", start_date="2025-12-01", end_date="2025-12-13")

        self.assertEqual(result["totalViews"], 10)
        mock_request.assert_called_once_with(
            "GET", "/analytics/content", None,
            {"assetId": "asset-1", "startDate": "2025-12-01", "endDate": "2025-12-13"},
        )


class TestCI360ContentDeliveryUpload(unittest.TestCase):
    """upload_asset_async/upload_asset - untested until now, and the
    method that turned up the missing requests-toolbelt dependency."""

    def setUp(self):
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_upload_asset_async_posts_multipart_and_returns_json(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        response = Mock(content=b'{"id": "asset-new"}')
        response.json.return_value = {"id": "asset-new"}
        mock_session.post.return_value = response

        client = CI360ContentDeliveryBase(self.config)
        result = asyncio.run(client.upload_asset_async({"name": "Banner"}, b"file-bytes", "banner.jpg"))

        self.assertEqual(result, {"id": "asset-new"})
        called_args, called_kwargs = mock_session.post.call_args
        self.assertIn("multipart/form-data", called_kwargs["headers"]["Content-Type"])
        # Regression: urljoin(host + api_base, "/assets/upload") drops api_base
        # too, since an absolute-path reference always replaces the whole path.
        self.assertEqual(called_args[0], "https://api.example.com/digital-assets/assets/upload")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_upload_asset_sync_delegates_to_async(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        response = Mock(content=b'{"id": "asset-new"}')
        response.json.return_value = {"id": "asset-new"}
        mock_session.post.return_value = response

        client = CI360ContentDeliveryBase(self.config)
        result = client.upload_asset({"name": "Banner"}, b"file-bytes", "banner.jpg")

        self.assertEqual(result["id"], "asset-new")

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_upload_asset_sync_logs_and_reraises_on_failure(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.post.side_effect = requests.exceptions.ConnectionError("refused")

        client = CI360ContentDeliveryBase(self.config)

        with self.assertRaises(requests.exceptions.ConnectionError):
            client.upload_asset({"name": "Banner"}, b"file-bytes", "banner.jpg")


class TestCI360ContentDeliveryContextManagers(unittest.TestCase):
    """__enter__/__exit__/__aenter__/__aexit__."""

    def setUp(self):
        self.config = CI360ContentDeliveryConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_sync_context_manager_success(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        with CI360ContentDeliveryBase(self.config) as client:
            self.assertTrue(client._connected)
        mock_session.close.assert_called_once()

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_sync_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        with self.assertRaises(CI360ContentDeliveryConnectionError):
            with CI360ContentDeliveryBase(self.config):
                pass

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_async_context_manager_success(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = Mock(status_code=200)

        async def _run():
            async with CI360ContentDeliveryBase(self.config) as client:
                return client._connected

        self.assertTrue(asyncio.run(_run()))
        mock_session.close.assert_called_once()

    @patch('sasci360solcontentdelivery.base.requests.Session')
    @patch('sasci360apicore.encryption.Encryption')
    def test_async_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = Mock(status_code=503)

        async def _run():
            async with CI360ContentDeliveryBase(self.config):
                pass

        with self.assertRaises(CI360ContentDeliveryConnectionError):
            asyncio.run(_run())


if __name__ == '__main__':
    unittest.main()
