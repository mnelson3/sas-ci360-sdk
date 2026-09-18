#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging


class Logger:
	def __init__(self):
		self.log_file = None
		self.logger = None

	def logging(self, log_file):
		self.log_file = log_file
		try:
			self.logger = logging.getLogger(__name__)
			self.logger.setLevel(logging.INFO)

			handler = logging.FileHandler(self.log_file)
			handler.setLevel(logging.INFO)

			self.logger.addHandler(handler)
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return self.logger


if __name__ == "__main__":
	Logger()
