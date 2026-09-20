#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import unittest

from sasci360apicore import encryption


class TestEncryption(unittest.TestCase):
	def setUp(self):
		self.log_file_path = "logs/encryption.log"

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

		self.encryption = encryption.Encryption(
			algorithm=self.algorithm,
			encoding=self.encoding)

	def tearDown(self):
		pass

	def test_generate_jwt_development(self):
		algorithm = self.algorithm
		encoding = self.encoding
		secret_key = self.secret_key_dev
		tenant_id = self.tenant_id_dev

		self.assertEqual(algorithm, "HS256")
		self.assertEqual(encoding, "UTF-8")
		self.assertEqual(secret_key, "example-secret-key-dev")
		self.assertEqual(tenant_id, "example-tenant-id-dev")

		result = self.encryption.generate_jwt(tenant_id=tenant_id, secret_key=secret_key)
		self.assertEqual(result, self.dev_token)

	def test_generate_jwt_test(self):
		algorithm = self.algorithm
		encoding = self.encoding
		secret_key = self.secret_key_test
		tenant_id = self.tenant_id_test

		self.assertEqual(algorithm, "HS256")
		self.assertEqual(encoding, "UTF-8")
		self.assertEqual(secret_key, "example-secret-key-test")
		self.assertEqual(tenant_id, "example-tenant-id-test")

		result = self.encryption.generate_jwt(tenant_id=tenant_id, secret_key=secret_key)
		self.assertEqual(result, self.test_token)

	def test_generate_jwt_production(self):
		algorithm = self.algorithm
		encoding = self.encoding
		secret_key = self.secret_key_prod
		tenant_id = self.tenant_id_prod

		self.assertEqual(algorithm, "HS256")
		self.assertEqual(encoding, "UTF-8")
		self.assertEqual(secret_key, "example-secret-key-prod")
		self.assertEqual(tenant_id, "example-tenant-id-prod")

		result = self.encryption.generate_jwt(tenant_id=tenant_id, secret_key=secret_key)
		self.assertEqual(result, self.prod_token)


if __name__ == "main":
	unittest.main()
