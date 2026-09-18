#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import time
import unittest

from sasci360apicore import listener


class TestListener(unittest.TestCase):
	def setUp(self):
		self.log_file_path = "logs/listener.log"
		self.source_file = ""
		self.source_path = ""
		self.destination_file = ""
		self.destination_path = ""
		self.sleep_seconds = 60

		self.listener = listener.Listener(
			source_file=self.source_file,
			source_path=self.source_path,
			destination_file=self.destination_file,
			destination_path=self.destination_path,
			sleep=self.sleep_seconds
		)

	def tearDown(self):
		pass

	def test_listener_run(self):
		# self.assertIsNotNone(path.exists(source_file_path))
		# self.assertIsNone(path.exists(destination_file_path))

		self.listener.run()
		time.sleep(15)

		# self.assertIsNone(path.exists(source_file_path))
		# self.assertIsNotNone(path.exists(destination_file_path))


if __name__ == "main":
	unittest.main()
