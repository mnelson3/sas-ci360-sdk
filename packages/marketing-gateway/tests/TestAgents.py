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

import os
import unittest
from sasci360apimarketinggateway import agents


class TestAgents(unittest.TestCase):

	def setUp(self) -> None:
		algorithm = "HS256"
		api = "/marketingGateway"
		encoding = "UTF-8"
		host = "YOUR_TENANT_HOST"
		secret_key = "YOUR_SECRET_KEY"
		tenant_id = "YOUR_TENANT_ID"

		self.agents = agents.Agents(
			algorithm=algorithm,
			api=api,
			encoding=encoding,
			host=host,
			secret_key=secret_key,
			tenant_id=tenant_id
		)

	def test_get_diagnostics_agent(self):
		"""
		1. get_diagnostics_agent(self) -> requests.Response
		"""
		folder_path = os.path.join(os.path.dirname(__file__), "..", "downloads")
		result = self.agents.get_diagnostics_agent()
		with open(os.path.join(folder_path, "diagnostics_agent.zip"), mode="wb") as f:
			f.write(result.content)
			f.flush()

	def test_get_direct_agent(self):
		"""
		2. get_direct_agent(self) -> requests.Response
		"""
		folder_path = os.path.join(os.path.dirname(__file__), "..", "downloads")
		result = self.agents.get_direct_agent()
		with open(os.path.join(folder_path, "direct_agent.zip"), mode="wb") as f:
			f.write(result.content)
			f.flush()

	def test_get_general_agent(self):
		"""
		3. get_general_agent(self) -> requests.Response
		"""
		folder_path = os.path.join(os.path.dirname(__file__), "..", "downloads")
		result = self.agents.get_general_agent()
		with open(os.path.join(folder_path, "general_agent.zip"), mode="wb") as f:
			f.write(result.content)
			f.flush()

	def test_get_optimize_agent(self):
		"""
		4. get_optimize_agent(self) -> requests.Response
		"""
		folder_path = os.path.join(os.path.dirname(__file__), "..", "downloads")
		result = self.agents.get_optimize_agent()
		with open(os.path.join(folder_path, "optimize_agent.zip"), mode="wb") as f:
			f.write(result.content)
			f.flush()


if __name__ == "__main__":
	unittest.main()
