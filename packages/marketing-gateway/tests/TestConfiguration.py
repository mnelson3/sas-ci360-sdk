#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Configuration Module
Contains the operations to see your API configuration
	1. get_configuration(self) -> requests.Response
"""

import unittest
from sasci360apimarketinggateway import configuration


class TestConfiguration(unittest.TestCase):

	def setUp(self) -> None:
		algorithm = "HS256"
		api = "/marketingGateway"
		encoding = "UTF-8"
		host = "YOUR_TENANT_HOST"
		secret_key = "YOUR_SECRET_KEY"
		tenant_id = "YOUR_TENANT_ID"

		self.configuration = configuration.Configuration(
			algorithm=algorithm,
			api=api,
			encoding=encoding,
			host=host,
			secret_key=secret_key,
			tenant_id=tenant_id
		)

	def test_get_configuration(self):
		"""
		1. get_configuration(self) -> requests.Response
		"""
		result = self.configuration.get_configuration()
		print("Result: {}".format(result))
		self.assertIsNotNone(result)


if __name__ == "__main__":
	unittest.main()
