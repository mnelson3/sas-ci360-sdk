#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
import time
import requests


class Connection:
	"""
	Connection Module
	Contains operations to connect to REST APIs
		1. def connect(self, **kwargs) -> requests.Response
	"""

	def __init__(self) -> None:
		self.logger = logging.getLogger(__name__)

	def connect(self, **kwargs) -> requests.Response:
		"""
		Connect
		:keywords action: str, required - method of operation to perform (DELETE, GET, PATCH, POST, PUT)
		:keywords data: dict, optional - package to be processed, valid with PATCH, POST, PUT actions
		:keywords headers: dict, required - an HTTP header that can be used in an HTTP request to provide information about the request context, so that the server can tailor the response
		:keywords params: str, optional - GET-style URL parameters, currently not implemented
		:keywords url: str, required - the web resource to access via HTTP(S) for the REST APIs
		:return: Returns requests.Response object
		:rtype: requests.Response
		"""
		result = None
		try:
			r = None
			action = None
			data = None
			headers = None
			params = None
			url = None

			if "action" in kwargs:
				action = kwargs["action"]
			if "data" in kwargs:
				data = kwargs["data"]
			if "headers" in kwargs:
				headers = kwargs["headers"]
			if "params" in kwargs:
				params = kwargs["params"]
			if "url" in kwargs:
				url = kwargs["url"]

			code = 500
			counter = 0
			while (not 200 <= code <= 299) and (counter < 3):
				time.sleep(3)
				if action == "DELETE":
					r = requests.delete(url=url, headers=headers)
				elif action == "GET":
					r = requests.get(url=url, params=params, headers=headers)
				elif action == "PATCH":
					r = requests.patch(url=url, data=data, headers=headers)
				elif action == "POST":
					r = requests.post(url=url, data=data, headers=headers)
				elif action == "PUT":
					r = requests.put(url=url, data=open(data, "rb"), headers=headers)
				counter += 1
				code = int(r.status_code)
			if 200 <= code <= 299:
				# 	if action == "PUT":
				# 		result = code
				# 	elif headers == "application/zip":
				# 		result = response.content
				# 	else:
				# 		result = response.json()
				# else:
				result = r
			r.close()
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return result


if __name__ == "__main__":
	Connection()
