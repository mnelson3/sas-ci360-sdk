#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Data Download Module
Contains the operations to download data tables for customer behavior, identities, metadata, and so on. The tables that you have access to are based on the licenses you have and the data that is available in the tables
	1. get_base_tables(self, **kwargs) -> requests.Response
	2. get_detail_tables(self, **kwargs) -> requests.Response
	3. get_identity_tables(self, **kwargs) -> requests.Response
	4. get_reprocessed_tables(self, **kwargs) -> requests.Response
"""

import unittest
from sasci360apimarketinggateway import data_download


class TestDataDownload(unittest.TestCase):

	def setUp(self) -> None:
		algorithm = "HS256"
		api = "/marketingGateway"
		encoding = "UTF-8"
		host = "YOUR_TENANT_HOST"
		secret_key = "YOUR_SECRET_KEY"
		tenant_id = "YOUR_TENANT_ID"

		self.data_download = data_download.DataDownload(
			algorithm=algorithm,
			api=api,
			encoding=encoding,
			host=host,
			secret_key=secret_key,
			tenant_id=tenant_id
		)

	def test_get_base_tables(self):
		"""
		1. get_base_tables(self, **kwargs) -> requests.Response
		"""
		result = self.data_download.get_base_tables()
		print("Result: {}".format(result))
		self.assertIsNotNone(result)

	def test_get_detail_tables(self):
		"""
		2. get_detail_tables(self, **kwargs) -> requests.Response
		"""
		result = self.data_download.get_detail_tables()
		print("Result: {}".format(result))
		self.assertIsNotNone(result)

	def test_get_identity_tables(self):
		"""
		3. get_identity_tables(self, **kwargs) -> requests.Response
		"""
		result = self.data_download.get_identity_tables()
		print("Result: {}".format(result))
		self.assertIsNotNone(result)

	def test_get_reprocessed_tables(self):
		"""
		4. get_reprocessed_tables(self, **kwargs) -> requests.Response
		"""
		result = self.data_download.get_reprocessed_tables()
		print("Result: {}".format(result))
		self.assertIsNotNone(result)


if __name__ == "__main__":
	unittest.main()
