#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import base64
import logging

import jwt


class Encryption:
	"""
	Encryption Module
	Contains operations to encrypt data
		1. def generate_jwt(self, **kwargs) -> str:
	"""

	def __init__(self, **kwargs) -> None:
		"""

		:keyword algorithm: str, required -
		:keyword encoding: str, required -
		"""
		self.logger = logging.getLogger(__name__)

		self.algorithm = kwargs["algorithm"]
		self.encoding = kwargs["encoding"]

	def generate_jwt(self, **kwargs) -> str:
		"""
		Generate JSON Web Token
		:keyword secret_key: str, required -
		:keyword tenant_id: str, required -
		:return:
		:rtype: str
		"""
		result = None
		try:
			algorithm = self.algorithm
			encoding = self.encoding

			secret_key = kwargs["secret_key"]
			tenant_id = kwargs["tenant_id"]

			payload = {"clientID": "{0}".format(tenant_id)}
			secret_key_bytes = bytes(str(secret_key), encoding=encoding)
			secret_key_encoded = base64.b64encode(secret_key_bytes)
			token = jwt.encode(payload=payload, key=secret_key_encoded, algorithm=algorithm)
			result = token
		except (KeyError, TypeError, LookupError, jwt.PyJWTError) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		return result


if __name__ == "__main__":
	Encryption()
