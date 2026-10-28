#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import base64
import unittest

import jwt

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

		self.encryption = encryption.Encryption(
			algorithm=self.algorithm,
			encoding=self.encoding)

	def tearDown(self):
		pass

	def assert_valid_token(self, token, secret_key, tenant_id):
		# Verify the token by decoding it instead of comparing to a stored sample.
		self.assertIsInstance(token, str)
		key = base64.b64encode(bytes(secret_key, encoding=self.encoding))
		payload = jwt.decode(token, key=key, algorithms=[self.algorithm])
		self.assertEqual(payload, {"clientID": tenant_id})

		# A different secret must not validate.
		with self.assertRaises(jwt.InvalidSignatureError):
			jwt.decode(token, key=b"wrong-key", algorithms=[self.algorithm])

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
		self.assert_valid_token(result, secret_key, tenant_id)

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
		self.assert_valid_token(result, secret_key, tenant_id)

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
		self.assert_valid_token(result, secret_key, tenant_id)


if __name__ == "main":
	unittest.main()
