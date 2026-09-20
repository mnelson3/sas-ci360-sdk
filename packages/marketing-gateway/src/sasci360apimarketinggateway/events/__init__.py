#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import requests
from sasci360apimarketinggateway.base import Base


class Events(Base):
	"""
	Events Module
	Contains operations to upload bulk events or inject single events
		1. create_bulk_events(self, payload: dict) -> requests.Response
		2. create_external_event(self, payload: dict) -> requests.Response
	"""

	def __init__(self, algorithm, api, encoding, host, secret_key, tenant_id) -> None:
		super().__init__(algorithm, api, encoding, host, secret_key, tenant_id)

	def create_bulk_events(self, payload: dict) -> requests.Response:
		"""
		Batch upload for external events
		:param payload: required - The JSON body that triggers the system to generate a URL
		:return: Submits a request to upload a file with external events. When you send this request with the appropriate JSON body, the response includes a signed, temporary URL. Use this URL to upload a bulk events file.
		:rtype: requests.Response
		"""
		token = self.token
		api = self.api
		host = self.host
		action = "POST"
		data = payload
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/bulkEventsFileLocation"
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)

	def create_external_event(self, payload: dict) -> requests.Response:
		"""
		Inject an external event
		:param payload: required - A string that contains an external event as a JSON object
		:return: Inject an external event into SAS Customer Intelligence 360. Define the external event in the JSON body of the request.
		:rtype: requests.Response
		"""
		token = self.token
		api = self.api
		host = self.host
		action = "POST"
		data = payload
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {0}".format(token)
		}
		params = None
		api_path = "/events"
		url = "https://{0}{1}{2}".format(host, api, api_path)
		return self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)

