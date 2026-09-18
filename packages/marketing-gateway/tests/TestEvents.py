#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Events Module
Contains operations to upload bulk events or inject single events
	1. create_bulk_events(self, payload: dict) -> requests.Response
	2. create_external_event(self, payload: dict) -> requests.Response
"""

import unittest
from sasci360apimarketinggateway import events


class TestEvents(unittest.TestCase):

	def setUp(self) -> None:
		algorithm = "HS256"
		api = "/marketingGateway"
		encoding = "UTF-8"
		host = "YOUR_TENANT_HOST"
		secret_key = "YOUR_SECRET_KEY"
		tenant_id = "YOUR_TENANT_ID"

		self.events = events.Events(
			algorithm=algorithm,
			api=api,
			encoding=encoding,
			host=host,
			secret_key=secret_key,
			tenant_id=tenant_id
		)

	def test_create_bulk_events(self):
		"""
		1. create_bulk_events(self, payload: dict) -> requests.Response
		"""
		payload = {
			"version": 1,
			"applicationId": "eventGenerator"
		}
		result = self.events.create_bulk_events(payload=payload)
		print("Result: {}".format(result))
		self.assertIsNotNone(result)

	def test_create_external_event(self):
		"""
		2. create_external_event(self, payload: dict) -> requests.Response
		"""
		payload = {
			"eventName": "eventExample",
			"subject_id": "267756",
			"Price": 100,
			"Month": "January"
		}
		result = self.events.create_external_event(payload=payload)
		print("Result: {}".format(result))
		self.assertIsNotNone(result)


if __name__ == "__main__":
	unittest.main()
