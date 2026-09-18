#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock, patch

from sasci360apicore import connection
from sasci360apicore import encryption


class TestConnection(unittest.TestCase):

	def setUp(self):
		self.log_file_path = "logs/connection.log"
		self.log_file_path_encrypt = "logs/encryption.log"

		self.algorithm = "HS256"
		self.encoding = "UTF-8"
		self.tenant_id_prod = "example-tenant-id-prod"
		self.tenant_id_test = "example-tenant-id-test"
		self.tenant_id_dev = "example-tenant-id-dev"
		self.secret_key_prod = "example-secret-key-prod"
		self.secret_key_test = "example-secret-key-test"
		self.secret_key_dev = "example-secret-key-dev"
		self.prod_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRJRCI6ImV4YW1wbGUtdGVuYW50LWlkLXByb2QifQ.h09P4T0LPJFuuDeTi4Wc3AIm6eNnj1-VCEZptuG01bM"
		self.test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRJRCI6ImV4YW1wbGUtdGVuYW50LWlkLXRlc3QifQ.8VdJikEWszK8qAHAntx8S9lJd3fHOySmfjLRaH9Mphs"
		self.dev_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRJRCI6ImV4YW1wbGUtdGVuYW50LWlkLWRldiJ9.ne2wL3tRdU7gNthU0nrdo3o3ayvpUuXeK43nU5N6b2A"
		self.external_gateway_path = "example.api.gateway.invalid"
		self.analytic_services_controller_path = "/marketingData/analytic"
		self.file_transfer_location_path = "/marketingData/fileTransferLocation"

		self.connection = connection.Connection()
		self.encryption = encryption.Encryption(
			algorithm=self.algorithm,
			encoding=self.encoding
		)

	def tearDown(self):
		pass

	def test_delete(self):
		pass

	@patch("requests.get")
	def test_get(self, mock_get):
		mock_get.return_value = MagicMock(status_code=200)
		algorithm = self.algorithm
		encoding = self.encoding
		secret_key = self.secret_key_dev
		tenant_id = self.tenant_id_dev

		print("algorithm : {0}".format(algorithm))
		self.assertEqual(algorithm, "HS256")
		print("encoding : {0}".format(encoding))
		self.assertEqual(encoding, "UTF-8")
		print("secret_key : {0}".format(secret_key))
		self.assertEqual(secret_key, "example-secret-key-dev")
		print("tenant_id : {0}".format(tenant_id))
		self.assertEqual(tenant_id, "example-tenant-id-dev")

		token = self.encryption.generate_jwt(secret_key=secret_key, tenant_id=tenant_id)
		self.assertEqual(token, self.dev_token)

		action = "GET"
		self.assertEqual(action, "GET")
		data = None
		self.assertIsNone(data)
		headers = {
			# "Accept": "application/vnd.sas.api+json",
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		self.assertEqual(
			headers,
			{
				# "Accept": "application/vnd.sas.api+json",
				"Content-Type": "application/json",
				"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRJRCI6ImV4YW1wbGUtdGVuYW50LWlkLWRldiJ9.ne2wL3tRdU7gNthU0nrdo3o3ayvpUuXeK43nU5N6b2A"
			}
		)
		params = None
		self.assertIsNone(params)
		url = "https://{0}{1}".format(
			self.external_gateway_path,
			self.analytic_services_controller_path
		)
		self.assertEqual(
			url,
			"https://example.api.gateway.invalid/marketingData/analytic"
		)
		result = self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)
		self.assertIsNotNone(result)
		print("result : {0}".format(result))

	def test_patch(self):
		pass

	@patch("requests.post")
	def test_post(self, mock_post):
		mock_post.return_value = MagicMock(status_code=200)
		secret_key = self.secret_key_dev
		print("secret_key : {0}".format(secret_key))
		tenant_id = self.tenant_id_dev
		print("tenant_id : {0}".format(tenant_id))

		token = self.encryption.generate_jwt(secret_key=secret_key, tenant_id=tenant_id)
		self.assertEqual(token, self.dev_token)

		action = "POST"
		self.assertEqual(action, "POST")
		data = None
		self.assertIsNone(data)
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		self.assertEqual(
			headers, {
				"Accept": "application/json",
				"Content-Type": "application/json",
				"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRJRCI6ImV4YW1wbGUtdGVuYW50LWlkLWRldiJ9.ne2wL3tRdU7gNthU0nrdo3o3ayvpUuXeK43nU5N6b2A"
			}
		)
		params = None
		self.assertIsNone(params)
		url = "https://{0}{1}".format(self.external_gateway_path, self.file_transfer_location_path)
		self.assertEqual(url, "https://example.api.gateway.invalid/marketingData/fileTransferLocation")
		result = self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)
		self.assertIsNotNone(result)
		print("result : {0}".format(result))

	def test_put(self):
		pass


if __name__ == "main":
	unittest.main()
