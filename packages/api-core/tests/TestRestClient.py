#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for sasci360apicore.rest_client.RestClientBase - the shared base class
every sol-* domain client's Base subclasses.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch

from sasci360apicore.rest_client import (
    RestClientBase,
    RestClientAuthError,
    RestClientConfig,
    RestClientConnectionError,
    RestClientValidationError,
)


class TestRestClientConfig(unittest.TestCase):
    def test_default_config(self):
        config = RestClientConfig()
        self.assertEqual(config.algorithm, "HS256")
        self.assertEqual(config.api_base, "")
        self.assertEqual(config.encoding, "utf-8")
        self.assertIsNone(config.host)
        self.assertIsNone(config.secret_key)
        self.assertIsNone(config.tenant_id)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_backoff, 0.5)
        self.assertTrue(config.enable_compression)


class TestRestClientBaseInit(unittest.TestCase):
    def setUp(self):
        self.config = RestClientConfig(
            host="https://api.example.com",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    def test_missing_required_fields_raises_validation_error(self):
        with self.assertRaises(RestClientValidationError):
            RestClientBase(RestClientConfig())

    def test_unsupported_algorithm_raises_validation_error(self):
        config = RestClientConfig(
            host="https://api.example.com", secret_key="s", tenant_id="t", algorithm="none"
        )
        with self.assertRaises(RestClientValidationError):
            RestClientBase(config)

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_initialization_success(self, mock_encryption_class, mock_session_class):
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption
        mock_session_class.return_value = Mock()

        client = RestClientBase(self.config)

        self.assertEqual(client.config, self.config)
        self.assertEqual(client.token, "test-token")
        self.assertFalse(client._connected)

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption", None)
    def test_generate_token_raises_auth_error_when_encryption_unavailable(self, mock_session_class):
        with self.assertRaises(RestClientAuthError):
            RestClientBase(self.config)

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_generate_token_raises_auth_error_when_jwt_is_none(self, mock_encryption_class, mock_session_class):
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = None
        mock_encryption_class.return_value = mock_encryption
        mock_session_class.return_value = Mock()

        with self.assertRaises(RestClientAuthError):
            RestClientBase(self.config)

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_get_auth_headers(self, mock_encryption_class, mock_session_class):
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption
        mock_session_class.return_value = Mock()

        client = RestClientBase(self.config)
        headers = client.get_auth_headers()

        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["X-Tenant-ID"], "test-tenant-id")


class TestRestClientBaseRequests(unittest.TestCase):
    def setUp(self):
        self.config = RestClientConfig(
            host="https://api.example.com",
            api_base="/marketingData",
            secret_key="test-secret-key",
            tenant_id="test-tenant-id",
        )

    def _make_client(self, mock_encryption_class, mock_session_class):
        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption
        mock_session_class.return_value = Mock()
        return RestClientBase(self.config)

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_make_request_async_includes_api_base_in_url(self, mock_encryption_class, mock_session_class):
        """The exact urljoin/api_base regression test - see docs/DDD.md.
        Pinned at the shared-base level now instead of once per package."""
        client = self._make_client(mock_encryption_class, mock_session_class)

        mock_response = Mock()
        mock_response.content = b'{"ok": true}'
        mock_response.json.return_value = {"ok": True}
        mock_response.raise_for_status.return_value = None
        client.session.request.return_value = mock_response
        client._connected = True

        asyncio.run(client._make_request_async("GET", "/customers"))

        called_url = client.session.request.call_args.kwargs["url"]
        self.assertEqual(called_url, "https://api.example.com/marketingData/customers")

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_make_request_async_not_connected_raises_connection_error(self, mock_encryption_class, mock_session_class):
        client = self._make_client(mock_encryption_class, mock_session_class)
        client.session.get.side_effect = OSError("no network")

        with self.assertRaises(RestClientConnectionError):
            asyncio.run(client._make_request_async("GET", "/customers"))

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    @patch("sasci360apicore.rest_client.RestClientBase._make_request_async")
    def test_make_request_sync_delegates_to_async(self, mock_request_async, mock_encryption_class, mock_session_class):
        async def fake_async(*args, **kwargs):
            return {"ok": True}
        mock_request_async.side_effect = fake_async

        client = self._make_client(mock_encryption_class, mock_session_class)
        result = client._make_request("GET", "/customers")

        self.assertEqual(result, {"ok": True})

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_validate_connection_async_hits_default_health_endpoint(self, mock_encryption_class, mock_session_class):
        client = self._make_client(mock_encryption_class, mock_session_class)

        mock_response = Mock()
        mock_response.status_code = 200
        client.session.get.return_value = mock_response

        result = asyncio.run(client.validate_connection_async())

        self.assertTrue(result)
        called_url = client.session.get.call_args.kwargs.get("url") or client.session.get.call_args.args[0]
        self.assertEqual(called_url, "https://api.example.com/health")

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_validate_connection_sync_wraps_async(self, mock_encryption_class, mock_session_class):
        client = self._make_client(mock_encryption_class, mock_session_class)

        mock_response = Mock()
        mock_response.status_code = 200
        client.session.get.return_value = mock_response

        self.assertTrue(client.validate_connection())

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_context_manager_closes_session_on_exit(self, mock_encryption_class, mock_session_class):
        client = self._make_client(mock_encryption_class, mock_session_class)
        client.session.get.return_value = Mock(status_code=200)

        with client as c:
            self.assertIs(c, client)

        client.session.close.assert_called_once()

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_context_manager_raises_when_connection_fails(self, mock_encryption_class, mock_session_class):
        client = self._make_client(mock_encryption_class, mock_session_class)
        client.session.get.side_effect = OSError("no network")

        with self.assertRaises(RestClientConnectionError):
            with client:
                pass


class TestRestClientBaseExtensionHooks(unittest.TestCase):
    """A subclass can override _CONFIG_CLS/_..._CLS/_validate_extra_config/
    _health_check_url without touching any shared behavior - exactly the
    contract every sol-* package's Base relies on."""

    def test_subclass_extra_validation_hook_is_called(self):
        class StrictConfig(RestClientConfig):
            pass

        class StrictError(RestClientValidationError):
            pass

        class StrictClient(RestClientBase):
            _VALIDATION_ERROR_CLS = StrictError

            def _validate_extra_config(self) -> None:
                raise self._VALIDATION_ERROR_CLS("extra check failed")

        config = StrictConfig(host="https://api.example.com", secret_key="s", tenant_id="t")
        with self.assertRaises(StrictError):
            StrictClient(config)

    @patch("sasci360apicore.rest_client.requests.Session")
    @patch("sasci360apicore.rest_client.Encryption")
    def test_subclass_health_check_url_override_is_used(self, mock_encryption_class, mock_session_class):
        class ScimClient(RestClientBase):
            def _health_check_url(self) -> str:
                return self._base_url.rstrip("/") + "/ServiceProviderConfig"

        mock_encryption = Mock()
        mock_encryption.generate_jwt.return_value = "test-token"
        mock_encryption_class.return_value = mock_encryption
        mock_session_class.return_value = Mock()

        config = RestClientConfig(
            host="https://api.example.com", api_base="/scim", secret_key="s", tenant_id="t"
        )
        client = ScimClient(config)
        client.session.get.return_value = Mock(status_code=200)

        asyncio.run(client.validate_connection_async())

        called_url = client.session.get.call_args.kwargs.get("url") or client.session.get.call_args.args[0]
        self.assertEqual(called_url, "https://api.example.com/scim/ServiceProviderConfig")


if __name__ == "__main__":
    unittest.main()
