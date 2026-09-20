#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Configuration Module
Contains the operations to see your API configuration
	1. get_configuration(self) -> requests.Response
"""

import unittest
from unittest.mock import MagicMock, patch

from sasci360apimarketinggateway import configuration


class TestConfiguration(unittest.TestCase):

	def setUp(self) -> None:
		self.algorithm = "HS256"
		self.api = "/marketingGateway"
		self.encoding = "UTF-8"
		self.host = "example.api.gateway.invalid"
		self.secret_key = "example-secret-key"
		self.tenant_id = "example-tenant-id"

		self.configuration = configuration.Configuration(
			algorithm=self.algorithm,
			api=self.api,
			encoding=self.encoding,
			host=self.host,
			secret_key=self.secret_key,
			tenant_id=self.tenant_id
		)

	@patch("requests.get")
	def test_get_configuration(self, mock_get):
		"""
		1. get_configuration(self) -> requests.Response
		"""
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"accessType": "trial"})

		result = self.configuration.get_configuration()

		self.assertIsNotNone(result)
		self.assertEqual(result, {"accessType": "trial"})
		called_kwargs = mock_get.call_args.kwargs
		self.assertEqual(called_kwargs["url"], "https://{0}{1}/configuration".format(self.host, self.api))


if __name__ == "__main__":
	unittest.main()
