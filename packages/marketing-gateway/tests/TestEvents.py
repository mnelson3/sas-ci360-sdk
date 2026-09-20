#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
Events Module
Contains operations to upload bulk events or inject single events
	1. create_bulk_events(self, payload: dict) -> requests.Response
	2. create_external_event(self, payload: dict) -> requests.Response
"""

import unittest
from unittest.mock import MagicMock, patch

from sasci360apimarketinggateway import events


class TestEvents(unittest.TestCase):

	def setUp(self) -> None:
		self.algorithm = "HS256"
		self.api = "/marketingGateway"
		self.encoding = "UTF-8"
		self.host = "example.api.gateway.invalid"
		self.secret_key = "example-secret-key"
		self.tenant_id = "example-tenant-id"

		self.events = events.Events(
			algorithm=self.algorithm,
			api=self.api,
			encoding=self.encoding,
			host=self.host,
			secret_key=self.secret_key,
			tenant_id=self.tenant_id
		)

	@patch("requests.post")
	def test_create_bulk_events(self, mock_post):
		"""
		1. create_bulk_events(self, payload: dict) -> requests.Response
		"""
		mock_post.return_value = MagicMock(status_code=200, json=lambda: {"signedURL": "https://example.invalid/upload"})
		payload = {
			"version": 1,
			"applicationId": "eventGenerator"
		}

		result = self.events.create_bulk_events(payload=payload)

		self.assertEqual(result, {"signedURL": "https://example.invalid/upload"})
		called_kwargs = mock_post.call_args.kwargs
		self.assertEqual(called_kwargs["url"], "https://{0}{1}/bulkEventsFileLocation".format(self.host, self.api))
		self.assertEqual(called_kwargs["data"], payload)

	@patch("requests.post")
	def test_create_external_event(self, mock_post):
		"""
		2. create_external_event(self, payload: dict) -> requests.Response
		"""
		mock_post.return_value = MagicMock(status_code=200, json=lambda: {"status": "accepted"})
		payload = {
			"eventName": "eventExample",
			"subject_id": "267756",
			"Price": 100,
			"Month": "January"
		}

		result = self.events.create_external_event(payload=payload)

		self.assertEqual(result, {"status": "accepted"})
		called_kwargs = mock_post.call_args.kwargs
		self.assertEqual(called_kwargs["url"], "https://{0}{1}/events".format(self.host, self.api))
		self.assertEqual(called_kwargs["data"], payload)


if __name__ == "__main__":
	unittest.main()
