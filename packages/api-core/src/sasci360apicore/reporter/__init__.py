#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import json
import logging
from pathlib import Path
from typing import Optional


class Reporter:
	"""

	"""

	def __init__(self, **kwargs) -> None:
		"""

		:keyword root:

		"""
		self.logger = logging.getLogger(__name__)

		self.root = kwargs["root"]

	def save(self, **kwargs) -> Optional[Path]:
		"""
		Save
		:keyword folder:
		:keyword name:
		:keyword data:
		:return:
		:rtype: Optional[Path]
		"""
		root = self.root
		json_file = None
		try:
			folder = kwargs["folder"]
			name = kwargs["name"]
			data = kwargs["data"]
			json_file = Path("{0}{1}{2}{3}".format(root, folder, name, ".JSON"))
			json_file.parent.mkdir(parents=True, exist_ok=True)
			with open(json_file, "w", encoding="utf-8") as outfile:
				json.dump(data, outfile, ensure_ascii=False, indent=4)
		except (KeyError, OSError, TypeError) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		return json_file


if __name__ == "__main__":
	Reporter()
