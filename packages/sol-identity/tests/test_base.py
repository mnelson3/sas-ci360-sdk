#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for SAS CI360 Identity Module

Comprehensive test suite for the CI360IdentityBase class and its APIs.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from sasci360solidentity.base import (
    CI360IdentityAuthError,
    CI360IdentityBase,
    CI360IdentityConfig,
    CI360IdentityError,
    CI360IdentityValidationError,
)


class TestCI360IdentityConfig(unittest.TestCase):
    """Test cases for CI360IdentityConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CI360IdentityConfig()
        self.assertEqual(config.algorithm, "HS256")
        self.assertEqual(config.api_base, "/scim")
        self.assertEqual(config.encoding, "utf-8")
        self.assertIsNone(config.host)
        self.assertIsNone(config.secret_key)
        self.assertIsNone(config.tenant_id)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_backoff, 0.5)
        self.assertTrue(config.enable_compression)
        self.assertEqual(config.scim_version, "2.0")

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CI360IdentityConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            timeout=60,
            scim_version="1.1"
        )
        self.assertEqual(config.host, "https://api.example.com")
        self.assertEqual(config.secret_key, "test-secret")
        self.assertEqual(config.tenant_id, "test-tenant")
        self.assertEqual(config.timeout, 60)
        self.assertEqual(config.scim_version, "1.1")


class TestCI360IdentityConfigValidation(unittest.TestCase):
    """Test cases for configuration validation performed on client init."""

    @patch('sasci360apicore.rest_client.Encryption')
    def test_missing_required_fields_raises(self, mock_encryption_class):
        """Missing host/secret_key/tenant_id should raise a validation error."""
        with self.assertRaises(CI360IdentityValidationError):
            CI360IdentityBase(CI360IdentityConfig())

    @patch('sasci360apicore.rest_client.Encryption')
    def test_unsupported_algorithm_raises(self, mock_encryption_class):
        """An unsupported JWT algorithm should raise a validation error."""
        config = CI360IdentityConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            algorithm="none"
        )
        with self.assertRaises(CI360IdentityValidationError):
            CI360IdentityBase(config)

    @patch('sasci360apicore.rest_client.Encryption')
    def test_unsupported_scim_version_raises(self, mock_encryption_class):
        """An unsupported SCIM version should raise a validation error."""
        config = CI360IdentityConfig(
            host="https://api.example.com",
            secret_key="test-secret",
            tenant_id="test-tenant",
            scim_version="3.0"
        )
        with self.assertRaises(CI360IdentityValidationError):
            CI360IdentityBase(config)


class TestCI360IdentityBase(unittest.TestCase):
    """Test cases for CI360IdentityBase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360IdentityConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_initialization_success(self, mock_encryption_class, mock_session_class):
        """Test successful initialization."""
        mock_encryption = MagicMock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption

        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = CI360IdentityBase(self.config)

        self.assertEqual(client.config, self.config)
        self.assertEqual(client.token, "test-token")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_get_auth_headers(self, mock_encryption_class, mock_session_class):
        """Test that auth headers are built from the generated token and config."""
        mock_encryption = MagicMock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption

        client = CI360IdentityBase(self.config)
        headers = client.get_auth_headers()

        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["X-Tenant-ID"], "test-tenant-id")
        self.assertEqual(headers["SCIM-Version"], "2.0")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_generate_token_wraps_any_failure_as_auth_error(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.side_effect = RuntimeError("bad key")

        with self.assertRaises(CI360IdentityAuthError):
            CI360IdentityBase(self.config)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_true_on_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = MagicMock(status_code=200)

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertTrue(result)
        self.assertTrue(client._connected)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_false_on_non_200(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = MagicMock(status_code=503)

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.validate_connection_async())

        self.assertFalse(result)
        self.assertFalse(client._connected)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_false_when_session_raises(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.side_effect = ConnectionError("refused")

        client = CI360IdentityBase(self.config)

        self.assertFalse(asyncio.run(client.validate_connection_async()))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_sync_delegates_to_async(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = MagicMock(status_code=200)

        client = CI360IdentityBase(self.config)

        self.assertTrue(client.validate_connection())

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360apicore.rest_client.asyncio.run')
    def test_validate_connection_sync_false_when_asyncio_run_raises(
        self, mock_asyncio_run, mock_encryption_class, mock_session_class
    ):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360IdentityBase(self.config)
        mock_asyncio_run.side_effect = RuntimeError("loop already running")

        self.assertFalse(client.validate_connection())

    def _connected_client(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360IdentityBase(self.config)
        client._connected = True
        return client, mock_session_class.return_value

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_returns_parsed_json_on_success(self, mock_encryption_class, mock_session_class):
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = MagicMock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/Users"))

        self.assertEqual(result, {"ok": True})

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_reconnects_when_not_connected(self, mock_encryption_class, mock_session_class):
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360IdentityBase(self.config)
        mock_session = mock_session_class.return_value
        mock_session.get.return_value = MagicMock(status_code=200)
        response = MagicMock(content=b'{"ok": true}')
        response.json.return_value = {"ok": True}
        mock_session.request.return_value = response

        result = asyncio.run(client._make_request_async("GET", "/Users"))

        self.assertEqual(result, {"ok": True})
        mock_session.get.assert_called_once()

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_raises_connection_error_when_reconnect_fails(
        self, mock_encryption_class, mock_session_class
    ):
        from sasci360solidentity.base import CI360IdentityConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360IdentityBase(self.config)
        mock_session_class.return_value.get.return_value = MagicMock(status_code=503)

        with self.assertRaises(CI360IdentityConnectionError):
            asyncio.run(client._make_request_async("GET", "/Users"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_401_raises_auth_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = MagicMock(status_code=401)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("401")
        mock_session.request.return_value = response

        with self.assertRaises(CI360IdentityAuthError):
            asyncio.run(client._make_request_async("GET", "/Users"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_5xx_raises_connection_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solidentity.base import CI360IdentityConnectionError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = MagicMock(status_code=503)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("503")
        mock_session.request.return_value = response

        with self.assertRaises(CI360IdentityConnectionError):
            asyncio.run(client._make_request_async("GET", "/Users"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_other_4xx_raises_generic_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        response = MagicMock(status_code=404)
        response.raise_for_status.side_effect = requests_module.exceptions.HTTPError("404")
        mock_session.request.return_value = response

        with self.assertRaises(CI360IdentityError):
            asyncio.run(client._make_request_async("GET", "/Users"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_network_error_raises_connection_error(self, mock_encryption_class, mock_session_class):
        import requests as requests_module
        from sasci360solidentity.base import CI360IdentityConnectionError
        client, mock_session = self._connected_client(mock_encryption_class, mock_session_class)
        mock_session.request.side_effect = requests_module.exceptions.ConnectionError("refused")

        with self.assertRaises(CI360IdentityConnectionError):
            asyncio.run(client._make_request_async("GET", "/Users"))

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_make_request_sync_logs_and_reraises(self, mock_request_async, mock_encryption_class, mock_session_class):
        from sasci360solidentity.base import CI360IdentityConnectionError
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        client = CI360IdentityBase(self.config)
        mock_request_async.side_effect = CI360IdentityConnectionError("down")

        with self.assertRaises(CI360IdentityConnectionError):
            client._make_request("GET", "/Users")

    # User Management Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_users_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async user retrieval."""
        mock_request.return_value = {"Resources": [], "totalResults": 0}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.get_users_async(limit=10, offset=5))

        self.assertEqual(result, {"Resources": [], "totalResults": 0})
        mock_request.assert_called_once_with(
            "GET", "/Users",
            params={"limit": 10, "offset": 5}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_user_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async single user retrieval."""
        user_data = {"id": "user-123", "userName": "john.doe", "name": {"givenName": "John", "familyName": "Doe"}}
        mock_request.return_value = user_data

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.get_user_async("user-123"))

        self.assertEqual(result["userName"], "john.doe")
        mock_request.assert_called_once_with("GET", "/Users/user-123")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_create_user_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async user creation."""
        user_data = {
            "userName": "john.doe",
            "name": {"givenName": "John", "familyName": "Doe"},
            "emails": [{"value": "john.doe@example.com", "primary": True}]
        }
        mock_request.return_value = {"id": "user-123", **user_data}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.create_user_async(user_data))

        self.assertEqual(result["id"], "user-123")
        mock_request.assert_called_once_with("POST", "/Users", data=user_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_update_user_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async user update."""
        update_data = {"name": {"givenName": "Jane", "familyName": "Doe"}}
        mock_request.return_value = {"id": "user-123", "userName": "john.doe", **update_data}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.update_user_async("user-123", update_data))

        self.assertEqual(result["name"]["givenName"], "Jane")
        mock_request.assert_called_once_with("PUT", "/Users/user-123", data=update_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_patch_user_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async user patch (SCIM)."""
        patch_data = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": [{"op": "replace", "path": "name.givenName", "value": "Jane"}]
        }
        mock_request.return_value = {"id": "user-123", "name": {"givenName": "Jane"}}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.patch_user_async("user-123", patch_data))

        self.assertEqual(result["name"]["givenName"], "Jane")
        mock_request.assert_called_once_with("PATCH", "/Users/user-123", data=patch_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_delete_user_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async user deletion."""
        mock_request.return_value = None

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.delete_user_async("user-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/Users/user-123")

    # Group Management Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_groups_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async group retrieval."""
        mock_request.return_value = {"Resources": [], "totalResults": 0}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.get_groups_async(limit=20, offset=10))

        self.assertEqual(result, {"Resources": [], "totalResults": 0})
        mock_request.assert_called_once_with(
            "GET", "/Groups",
            params={"limit": 20, "offset": 10}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_create_group_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async group creation."""
        group_data = {
            "displayName": "Marketing Team",
            "members": [{"value": "user-123"}]
        }
        mock_request.return_value = {"id": "group-123", **group_data}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.create_group_async(group_data))

        self.assertEqual(result["displayName"], "Marketing Team")
        mock_request.assert_called_once_with("POST", "/Groups", data=group_data)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_delete_group_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async group deletion."""
        mock_request.return_value = None

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.delete_group_async("group-123"))

        self.assertTrue(result)
        mock_request.assert_called_once_with("DELETE", "/Groups/group-123")

    # Authentication Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_authenticate_user_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async user authentication."""
        credentials = {"userName": "john.doe", "password": "secret"}
        mock_request.return_value = {
            "accessToken": "jwt-token",
            "refreshToken": "refresh-token",
            "expiresIn": 3600
        }

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.authenticate_user_async(credentials))

        self.assertEqual(result["accessToken"], "jwt-token")
        mock_request.assert_called_once_with("POST", "/auth/authenticate", data=credentials)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_validate_token_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async token validation."""
        mock_request.return_value = {"valid": True, "userId": "user-123", "expiresAt": "2025-12-14T00:00:00Z"}

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.validate_token_async("jwt-token"))

        self.assertTrue(result["valid"])
        mock_request.assert_called_once_with("POST", "/auth/validate", data={"token": "jwt-token"})

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_refresh_token_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async token refresh."""
        mock_request.return_value = {
            "accessToken": "new-jwt-token",
            "refreshToken": "new-refresh-token",
            "expiresIn": 3600
        }

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.refresh_token_async("old-refresh-token"))

        self.assertEqual(result["accessToken"], "new-jwt-token")
        mock_request.assert_called_once_with("POST", "/auth/refresh", data={"refreshToken": "old-refresh-token"})

    # SCIM Service Provider Config Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_service_provider_config_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async SCIM service provider config retrieval."""
        config_data = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            "patch": {"supported": True},
            "bulk": {"supported": True, "maxOperations": 100},
            "filter": {"supported": True}
        }
        mock_request.return_value = config_data

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.get_service_provider_config_async())

        self.assertTrue(result["patch"]["supported"])
        mock_request.assert_called_once_with("GET", "/ServiceProviderConfig")

    # Bulk Operations Tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_bulk_operation_async(self, mock_request, mock_encryption_class, mock_session_class):
        """Test async bulk SCIM operations."""
        operations = [
            {
                "method": "POST",
                "path": "/Users",
                "data": {"userName": "user1", "name": {"givenName": "User", "familyName": "One"}}
            },
            {
                "method": "DELETE",
                "path": "/Users/user-123"
            }
        ]
        mock_request.return_value = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkResponse"],
            "Operations": [
                {"status": "201", "location": "/Users/user-456"},
                {"status": "204"}
            ]
        }

        client = CI360IdentityBase(self.config)
        result = asyncio.run(client.bulk_operation_async(operations))

        self.assertEqual(len(result["Operations"]), 2)
        expected_payload = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
            "Operations": operations
        }
        mock_request.assert_called_once_with("POST", "/Bulk", data=expected_payload)

    # Synchronous method tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_users_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous user retrieval."""
        mock_request.return_value = {"Resources": [], "totalResults": 0}

        client = CI360IdentityBase(self.config)
        result = client.get_users(limit=10)

        self.assertEqual(result["totalResults"], 0)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_create_user_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous user creation."""
        user_data = {"userName": "john.doe"}
        mock_request.return_value = {"id": "user-123", **user_data}

        client = CI360IdentityBase(self.config)
        result = client.create_user(user_data)

        self.assertEqual(result["id"], "user-123")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_authenticate_user_sync(self, mock_request, mock_encryption_class, mock_session_class):
        """Test synchronous user authentication."""
        credentials = {"userName": "john.doe", "password": "secret"}
        mock_request.return_value = {"accessToken": "jwt-token"}

        client = CI360IdentityBase(self.config)
        result = client.authenticate_user(credentials)

        self.assertEqual(result["accessToken"], "jwt-token")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_users_sync_merges_filters(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"Resources": []}
        client = CI360IdentityBase(self.config)

        client.get_users(limit=10, offset=5, filters={"active": True})

        mock_request.assert_called_once_with(
            "GET", "/Users", None, {"limit": 10, "offset": 5, "active": True}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_users_async_merges_filters(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"Resources": []}
        client = CI360IdentityBase(self.config)

        asyncio.run(client.get_users_async(filters={"active": True}))

        mock_request.assert_called_once_with(
            "GET", "/Users", params={"limit": 100, "offset": 0, "active": True}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_user_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "user-1"}
        client = CI360IdentityBase(self.config)

        client.get_user("user-1")

        mock_request.assert_called_once_with("GET", "/Users/user-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_update_user_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "user-1"}
        client = CI360IdentityBase(self.config)

        client.update_user("user-1", {"name": {"givenName": "Jane"}})

        mock_request.assert_called_once_with("PUT", "/Users/user-1", {"name": {"givenName": "Jane"}}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_patch_user_async_and_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "user-1"}
        client = CI360IdentityBase(self.config)
        patch_data = {"Operations": []}

        asyncio.run(client.patch_user_async("user-1", patch_data))
        mock_request.assert_called_with("PATCH", "/Users/user-1", data=patch_data)

        client.patch_user("user-1", patch_data)
        mock_request.assert_called_with("PATCH", "/Users/user-1", patch_data, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_delete_user_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = None
        client = CI360IdentityBase(self.config)

        self.assertTrue(client.delete_user("user-1"))
        mock_request.assert_called_once_with("DELETE", "/Users/user-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_groups_sync_merges_filters(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"Resources": []}
        client = CI360IdentityBase(self.config)

        client.get_groups(limit=20, offset=10, filters={"displayName": "Marketing"})

        mock_request.assert_called_once_with(
            "GET", "/Groups", None, {"limit": 20, "offset": 10, "displayName": "Marketing"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_groups_async_merges_filters(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"Resources": []}
        client = CI360IdentityBase(self.config)

        asyncio.run(client.get_groups_async(filters={"displayName": "Marketing"}))

        mock_request.assert_called_once_with(
            "GET", "/Groups", params={"limit": 100, "offset": 0, "displayName": "Marketing"}
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_group_async_and_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "group-1"}
        client = CI360IdentityBase(self.config)

        asyncio.run(client.get_group_async("group-1"))
        mock_request.assert_called_with("GET", "/Groups/group-1")

        client.get_group("group-1")
        mock_request.assert_called_with("GET", "/Groups/group-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_create_group_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "group-1"}
        client = CI360IdentityBase(self.config)

        client.create_group({"displayName": "Team"})

        mock_request.assert_called_once_with("POST", "/Groups", {"displayName": "Team"}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_update_group_async_and_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"id": "group-1"}
        client = CI360IdentityBase(self.config)

        asyncio.run(client.update_group_async("group-1", {"displayName": "New"}))
        mock_request.assert_called_with("PUT", "/Groups/group-1", data={"displayName": "New"})

        client.update_group("group-1", {"displayName": "New"})
        mock_request.assert_called_with("PUT", "/Groups/group-1", {"displayName": "New"}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_delete_group_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = None
        client = CI360IdentityBase(self.config)

        self.assertTrue(client.delete_group("group-1"))
        mock_request.assert_called_once_with("DELETE", "/Groups/group-1", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_validate_token_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"valid": True}
        client = CI360IdentityBase(self.config)

        result = client.validate_token("jwt-token")

        self.assertTrue(result["valid"])
        mock_request.assert_called_once_with("POST", "/auth/validate", {"token": "jwt-token"}, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_refresh_token_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"accessToken": "new-token"}
        client = CI360IdentityBase(self.config)

        client.refresh_token("old-refresh-token")

        mock_request.assert_called_once_with(
            "POST", "/auth/refresh", {"refreshToken": "old-refresh-token"}, None
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_get_service_provider_config_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"patch": {"supported": True}}
        client = CI360IdentityBase(self.config)

        result = client.get_service_provider_config()

        self.assertTrue(result["patch"]["supported"])
        mock_request.assert_called_once_with("GET", "/ServiceProviderConfig", None, None)

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_bulk_operation_sync(self, mock_request, mock_encryption_class, mock_session_class):
        mock_request.return_value = {"Operations": []}
        client = CI360IdentityBase(self.config)
        operations = [{"method": "DELETE", "path": "/Users/user-1"}]

        client.bulk_operation(operations)

        mock_request.assert_called_once_with(
            "POST", "/Bulk",
            {"schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"], "Operations": operations},
            None,
        )

    # Context manager tests

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase.validate_connection')
    def test_context_manager_success(self, mock_validate, mock_encryption_class, mock_session_class):
        """Test sync context manager enters when the connection validates."""
        mock_validate.return_value = True
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        with CI360IdentityBase(self.config) as client:
            self.assertIsInstance(client, CI360IdentityBase)

        mock_session.close.assert_called_once()

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase.validate_connection')
    def test_context_manager_connection_failure(self, mock_validate, mock_encryption_class, mock_session_class):
        """Test sync context manager raises when the connection fails to validate."""
        mock_validate.return_value = False

        with self.assertRaises(Exception):
            with CI360IdentityBase(self.config):
                pass

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase.validate_connection_async')
    def test_async_context_manager_success(self, mock_validate, mock_encryption_class, mock_session_class):
        async def _mock_validate():
            return True
        mock_validate.side_effect = _mock_validate
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        async def _run():
            async with CI360IdentityBase(self.config) as client:
                return client

        client = asyncio.run(_run())

        self.assertIsInstance(client, CI360IdentityBase)
        mock_session.close.assert_called_once()

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase.validate_connection_async')
    def test_async_context_manager_connection_failure(self, mock_validate, mock_encryption_class, mock_session_class):
        from sasci360solidentity.base import CI360IdentityConnectionError

        async def _mock_validate():
            return False
        mock_validate.side_effect = _mock_validate

        async def _run():
            async with CI360IdentityBase(self.config):
                pass

        with self.assertRaises(CI360IdentityConnectionError):
            asyncio.run(_run())


class TestCI360IdentityErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = CI360IdentityConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id"
        )

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    @patch('sasci360solidentity.base.CI360IdentityBase._make_request_async')
    def test_auth_error_handling(self, mock_request, mock_encryption_class, mock_session_class):
        """Test authentication error handling."""
        mock_request.side_effect = CI360IdentityAuthError("Invalid credentials")

        client = CI360IdentityBase(self.config)

        with self.assertRaises(CI360IdentityAuthError):
            asyncio.run(client.authenticate_user_async({"userName": "invalid", "password": "wrong"}))

    # URL construction tests
    #
    # Every test above mocks _make_request_async itself, so none of them
    # ever exercise the URL it builds. That let a real bug through:
    # urljoin(host + api_base, endpoint) silently drops api_base, because
    # urljoin treats a base URL with no trailing slash as a document to
    # replace rather than a directory to extend under RFC 3986 relative
    # reference resolution (same bug already fixed in sol-planning,
    # sol-content-delivery, sol-data, sol-execute, and sol-workflow) -
    # and a second mechanism hit the SCIM ServiceProviderConfig health
    # check too, since urljoin also replaces the whole path whenever the
    # second argument is itself absolute (starts with "/"). These tests
    # mock one level deeper (the session's own .get/.request calls) to
    # pin down the actual URLs requested.

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_make_request_async_includes_api_base_in_url(self, mock_encryption_class, mock_session_class):
        """_make_request_async must build a URL under config.api_base, not just config.host."""
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_response = MagicMock()
        mock_response.content = b'{"ok": true}'
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status.return_value = None
        mock_session_class.return_value.request.return_value = mock_response

        client = CI360IdentityBase(self.config)
        client._connected = True

        asyncio.run(client._make_request_async("GET", "/Users"))

        called_url = mock_session_class.return_value.request.call_args.kwargs["url"]
        self.assertEqual(called_url, "https://api.example.com/scim/Users")

    @patch('sasci360apicore.rest_client.requests.Session')
    @patch('sasci360apicore.rest_client.Encryption')
    def test_validate_connection_async_checks_service_provider_config_under_api_base(
        self, mock_encryption_class, mock_session_class
    ):
        """The SCIM ServiceProviderConfig health check must stay under config.api_base too."""
        mock_encryption_class.return_value.generate_jwt.return_value = "test-token"
        mock_session_class.return_value.get.return_value = MagicMock(status_code=200)

        client = CI360IdentityBase(self.config)
        asyncio.run(client.validate_connection_async())

        called_url = mock_session_class.return_value.get.call_args.args[0]
        self.assertEqual(called_url, "https://api.example.com/scim/ServiceProviderConfig")


if __name__ == '__main__':
    unittest.main()
