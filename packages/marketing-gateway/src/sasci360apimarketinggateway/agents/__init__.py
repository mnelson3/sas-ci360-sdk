#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import requests
from sasci360apimarketinggateway.base import Base


class Agents(Base):
	"""
	Agents Module
	Contains the operations for downloading on-premises agents. To download the on-premises SDK, use the /agent endpoint to download the general agent (which includes the SDK)
		1. get_diagnostics_agent(self) -> requests.Response
		2. get_direct_agent(self) -> requests.Response
		3. get_general_agent(self) -> requests.Response
		4. get_optimize_agent(self) -> requests.Response
	"""

	def __init__(self, algorithm, api, encoding, host, secret_key, tenant_id) -> None:
		super().__init__(algorithm, api, encoding, host, secret_key, tenant_id)

	def get_diagnostics_agent(self) -> requests.Response:
		"""
		Download the diagnostics agent
		:return: Download the .zip file that contains the Diagnostics agent.
		:rtype: requests.Response
		"""
		result = None
		token = self.token
		api = self.api
		host = self.host
		try:
			action = "GET"
			data = None
			headers = {
				"Content-Type": "application/zip",
				"Authorization": "Bearer {0}".format(token)
			}
			params = None
			api_path = "/diag"
			url = "https://{0}{1}{2}".format(host, api, api_path)
			result = self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return result

	def get_direct_agent(self) -> requests.Response:
		"""
		Download the direct agent
		:return: Download the .zip file that contains the Direct agent.
		:rtype: requests.Response
		"""
		result = None
		token = self.token
		api = self.api
		host = self.host
		try:
			action = "GET"
			data = None
			headers = {
				"Content-Type": "application/zip",
				"Authorization": "Bearer {0}".format(token)
			}
			params = None
			api_path = "/satellite"
			url = "https://{0}{1}{2}".format(host, api, api_path)
			result = self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return result

	def get_general_agent(self) -> requests.Response:
		"""
		Download the general agent and the agent SDK
		:return: Download the .zip file that contains the General agent and the SDK for the on-premises agents.
		:rtype: requests.Response
		"""
		result = None
		token = self.token
		api = self.api
		host = self.host
		try:
			action = "GET"
			data = None
			headers = {
				"Content-Type": "application/zip",
				"Authorization": "Bearer {0}".format(token)
			}
			params = None
			api_path = "/agent"
			url = "https://{0}{1}{2}".format(host, api, api_path)
			result = self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return result

	def get_optimize_agent(self) -> requests.Response:
		"""
		Download the optimize agent
		:return: Download the .zip file that contains the Optimize agent.
		:rtype: requests.Response
		"""
		result = None
		token = self.token
		api = self.api
		host = self.host
		try:
			action = "GET"
			data = None
			headers = {
				"Content-Type": "application/zip",
				"Authorization": "Bearer {0}".format(token)
			}
			params = None
			api_path = "/optimize"
			url = "https://{0}{1}{2}".format(host, api, api_path)
			result = self.connection.connect(action=action, data=data, headers=headers, params=params, url=url)
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return result


if __name__ == "__main__":
	Agents()
