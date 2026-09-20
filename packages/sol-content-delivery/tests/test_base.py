#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SAS CI360 Content Delivery Module

Comprehensive test suite for the CI360ContentDeliveryBase class and its APIs.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

from sasci360solcontentdelivery.base import CI360ContentDeliveryBase, CI360ContentDeliveryConfig, CI360ContentDeliveryError


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


if __name__ == '__main__':
    unittest.main()