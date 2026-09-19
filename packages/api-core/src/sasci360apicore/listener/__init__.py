#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path


class Listener:
	"""

	"""

	def __init__(self, **kwargs) -> None:
		"""

		:keyword source_file:
		:keyword source_path:
		:keyword destination_file:
		:keyword destination_path:
		:keyword sleep:

		"""
		self.logger = logging.getLogger(__name__)

		self.source_file = kwargs["source_file"]
		self.source_path = kwargs["source_path"]
		self.destination_file = kwargs["destination_file"]
		self.destination_path = kwargs["destination_path"]
		self.sleep_seconds = kwargs["sleep"]

	def run(self) -> None:
		"""

		:return:
		"""
		sleep = self.sleep_seconds
		try:
			while True:
				time_stamp = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
				time_stamp_ = time_stamp.replace(":", "")
				source_file_path = Path("{0}/{1}".format(self.source_path, self.source_file))

				if Path.exists(source_file_path):
					file_export_chain = "{0}_{1}{2}".format(self.source_file[:-4], time_stamp_, ".CSV")
					file_export_chain_path = Path("{0}/{1}".format(self.destination_path, file_export_chain))
					shutil.copy(source_file_path, file_export_chain_path)

					if Path.exists(file_export_chain_path):
						os.remove(source_file_path)

				time.sleep(sleep)
		except OSError as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))


if __name__ == "__main__":
	Listener()
