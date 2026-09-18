#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import json
import logging
from pathlib import Path


class Reporter:
	"""

	"""

	def __init__(self, **kwargs) -> None:
		"""

		:keyword root:

		"""
		self.logger = logging.getLogger(__name__)

		self.root = kwargs["root"]

	def save(self, **kwargs) -> Path:
		"""
		Save
		:keyword folder:
		:keyword name:
		:keyword data:
		:return:
		:rtype: Path
		"""
		root = self.root
		json_file = None
		try:
			folder = kwargs["folder"]
			name = kwargs["name"]
			data = kwargs["data"]
			json_file = Path("{0}{1}{2}{3}".format(root, folder, name, ".JSON"))
			with open(json_file, "w", encoding="utf-8") as outfile:
				json.dump(data, outfile, ensure_ascii=False, indent=4)
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return json_file


if __name__ == "__main__":
	Reporter()
