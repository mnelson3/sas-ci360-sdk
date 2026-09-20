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
from unittest.mock import MagicMock, patch

from sasci360apimarketinggateway import data_download


class TestDataDownload(unittest.TestCase):

	def setUp(self) -> None:
		self.algorithm = "HS256"
		self.api = "/marketingGateway"
		self.encoding = "UTF-8"
		self.host = "example.api.gateway.invalid"
		self.secret_key = "example-secret-key"
		self.tenant_id = "example-tenant-id"

		self.data_download = data_download.DataDownload(
			algorithm=self.algorithm,
			api=self.api,
			encoding=self.encoding,
			host=self.host,
			secret_key=self.secret_key,
			tenant_id=self.tenant_id
		)

	@patch("requests.get")
	def test_get_base_tables_with_no_filters_omits_query_string(self, mock_get):
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"items": []})

		result = self.data_download.get_base_tables()

		self.assertEqual(result, {"items": []})
		url = mock_get.call_args.kwargs["url"]
		self.assertEqual(url, "https://{0}{1}/discoverService/dataDownload/eventData/dbtReport".format(self.host, self.api))

	@patch("requests.get")
	def test_get_base_tables_includes_requested_filters(self, mock_get):
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"items": []})

		self.data_download.get_base_tables(start=0, limit=100, schema_version=4)

		url = mock_get.call_args.kwargs["url"]
		self.assertIn("start=0&", url)
		self.assertIn("limit=100&", url)
		self.assertIn("schemaVersion=4", url)
		self.assertFalse(url.endswith("&"))

	@patch("requests.get")
	def test_get_detail_tables_includes_requested_filters(self, mock_get):
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"items": []})

		self.data_download.get_detail_tables(category="DISCOVER", include_all_hour_status=True)

		url = mock_get.call_args.kwargs["url"]
		self.assertIn("category=DISCOVER", url)
		self.assertIn("includeAllHourStatus=True&", url)
		self.assertFalse(url.endswith("&"))

	@patch("requests.get")
	def test_get_identity_tables_includes_requested_filters(self, mock_get):
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"items": []})

		self.data_download.get_identity_tables(start=10, limit=50)

		url = mock_get.call_args.kwargs["url"]
		self.assertIn("start=10&", url)
		self.assertIn("limit=50", url)
		self.assertFalse(url.endswith("&"))

	@patch("requests.get")
	def test_get_reprocessed_tables_includes_mart_type(self, mock_get):
		mock_get.return_value = MagicMock(status_code=200, json=lambda: {"items": []})

		self.data_download.get_reprocessed_tables(mart_type="identity", day_offset=1)

		url = mock_get.call_args.kwargs["url"]
		self.assertIn("martType=identity&", url)
		self.assertIn("dayOffset=1", url)
		self.assertFalse(url.endswith("&"))

	def test_get_reprocessed_tables_requires_mart_type(self):
		with self.assertRaises(ValueError):
			self.data_download.get_reprocessed_tables()


if __name__ == "__main__":
	unittest.main()
