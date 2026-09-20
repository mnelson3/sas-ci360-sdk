#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Agents Module
Contains the operations for downloading on-premises agents. To download the on-premises SDK, use the /agent endpoint to download the general agent (which includes the SDK)
	1. get_diagnostics_agent(self) -> requests.Response
	2. get_direct_agent(self) -> requests.Response
	3. get_general_agent(self) -> requests.Response
	4. get_optimize_agent(self) -> requests.Response
"""

import unittest
from unittest.mock import MagicMock, patch

from sasci360apimarketinggateway import agents


def _zip_response():
	# A real .zip download has no JSON body; Connection.connect() falls back
	# to raw bytes when response.json() raises.
	response = MagicMock(status_code=200)
	response.json.side_effect = ValueError("No JSON object could be decoded")
	response.content = b"PK\x03\x04fake-zip-bytes"
	return response


class TestAgents(unittest.TestCase):

	def setUp(self) -> None:
		self.algorithm = "HS256"
		self.api = "/marketingGateway"
		self.encoding = "UTF-8"
		self.host = "example.api.gateway.invalid"
		self.secret_key = "example-secret-key"
		self.tenant_id = "example-tenant-id"

		self.agents = agents.Agents(
			algorithm=self.algorithm,
			api=self.api,
			encoding=self.encoding,
			host=self.host,
			secret_key=self.secret_key,
			tenant_id=self.tenant_id
		)

	@patch("requests.get")
	def test_get_diagnostics_agent(self, mock_get):
		mock_get.return_value = _zip_response()

		result = self.agents.get_diagnostics_agent()

		self.assertEqual(result, b"PK\x03\x04fake-zip-bytes")
		self.assertEqual(mock_get.call_args.kwargs["url"], "https://{0}{1}/diag".format(self.host, self.api))

	@patch("requests.get")
	def test_get_direct_agent(self, mock_get):
		mock_get.return_value = _zip_response()

		result = self.agents.get_direct_agent()

		self.assertEqual(result, b"PK\x03\x04fake-zip-bytes")
		self.assertEqual(mock_get.call_args.kwargs["url"], "https://{0}{1}/satellite".format(self.host, self.api))

	@patch("requests.get")
	def test_get_general_agent(self, mock_get):
		mock_get.return_value = _zip_response()

		result = self.agents.get_general_agent()

		self.assertEqual(result, b"PK\x03\x04fake-zip-bytes")
		self.assertEqual(mock_get.call_args.kwargs["url"], "https://{0}{1}/agent".format(self.host, self.api))

	@patch("requests.get")
	def test_get_optimize_agent(self, mock_get):
		mock_get.return_value = _zip_response()

		result = self.agents.get_optimize_agent()

		self.assertEqual(result, b"PK\x03\x04fake-zip-bytes")
		self.assertEqual(mock_get.call_args.kwargs["url"], "https://{0}{1}/optimize".format(self.host, self.api))


if __name__ == "__main__":
	unittest.main()
