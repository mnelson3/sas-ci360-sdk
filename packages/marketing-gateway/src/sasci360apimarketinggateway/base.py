#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
from sasci360apicore import connection
from sasci360apicore import encryption


class Base:

	def __init__(self, algorithm, api, encoding, host, secret_key, tenant_id):
		self.logger = logging.getLogger(__name__)

		self.algorithm = algorithm
		self.api = api
		self.encoding = encoding
		self.host = host
		self.secret_key = secret_key
		self.tenant_id = tenant_id

		self.connection = connection.Connection()
		self.encryption = encryption.Encryption(algorithm=self.algorithm, encoding=self.encoding)
		self.token = self.encryption.generate_jwt(tenant_id=self.tenant_id, secret_key=self.secret_key)


if __name__ == "__main__":
	Base()
