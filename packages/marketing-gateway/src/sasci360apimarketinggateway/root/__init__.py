#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import requests
from sasci360apimarketinggateway.base import Base


class Root(Base):
	"""
	Root Module
	Contains the operations for this root resource
		1. get_root(self) -> requests.Response
	"""

	def __init__(self, algorithm, api, encoding, host, secret_key, tenant_id) -> None:
		super().__init__(algorithm, api, encoding, host, secret_key, tenant_id)

	def get_root(self) -> requests.Response:
		"""
		Get the links for the API
		:return: Returns the links to the top-level resources for the API.
		:rtype: requests.Response
		"""
		token = self.token
		api = self.api
		host = self.host
		action = "GET"
		data = None
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/"
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)

