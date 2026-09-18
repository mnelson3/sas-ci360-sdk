#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import unittest

from sasci360apicore import logger


class TestLogger(unittest.TestCase):
	def setUp(self):
		self.log_file_path = "logs/logger.log"
		self.logger = logger.Logger()

	def tearDown(self):
		pass

	def test_log(self):
		self.logger.logging(log_file=self.log_file_path)
		self.assertEqual(self.logger.log_file, "logs/logger.log")


if __name__ == "main":
	unittest.main()
