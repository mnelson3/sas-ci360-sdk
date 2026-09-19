#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Root Module
Contains the operations for this root resource
	1. get_root(self) -> requests.Response
"""

import unittest
from unittest.mock import MagicMock, patch

from sasci360apimarketinggateway import root


class TestRoot(unittest.TestCase):

	def setUp(self) -> None:
		self.algorithm = "HS256"
		self.api = "/marketingGateway"
		self.encoding = "UTF-8"
		self.host = "example.api.gateway.invalid"
		self.secret_key = "example-secret-key"
		self.tenant_id = "example-tenant-id"

		self.root = root.Root(
			algorithm=self.algorithm,
			api=self.api,
			encoding=self.encoding,
			host=self.host,
			secret_key=self.secret_key,
			tenant_id=self.tenant_id
		)

	@patch("requests.get")
	def test_get_root(self, mock_get):
		"""
		1. get_root(self) -> requests.Response
		"""
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"links": []})

		result = self.root.get_root()

		self.assertIsNotNone(result)
		self.assertEqual(result, {"links": []})
		called_kwargs = mock_get.call_args.kwargs
		self.assertEqual(called_kwargs["url"], "https://{0}{1}/".format(self.host, self.api))
		self.assertEqual(called_kwargs["headers"]["Content-Type"], "application/json")
		self.assertTrue(called_kwargs["headers"]["Authorization"].startswith("Bearer "))


if __name__ == "__main__":
	unittest.main()
