#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import unittest
from datetime import datetime

from sasci360apicore import reporter


class TestReporter(unittest.TestCase):
	def setUp(self):
		self.log_file_path = "logs/reporter.log"
		self.time_stamp = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
		self.root = "tests/data"
		self.reporter = reporter.Reporter(root=self.root)

	def tearDown(self):
		pass

	def test_save(self):
		# time_stamp = self.time_stamp.replace(":", "")
		# folder = "/response/"
		# filename = "table_get_{}".format(time_stamp)
		# r = ""  # JSON file downloaded from CI360
		# self.reporter.save(folder=folder, name=filename, data=r)
		pass


if __name__ == "main":
	unittest.main()
