#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import unittest

from sasci360apicore import scheduler


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.log_file_path = "logs/scheduler.log"
        self.object = ""
        self.minute = "00"
        self.hour = "02"
        self.day = "Monday"
        self.sleep = 300

        self.scheduler = scheduler.Scheduler(
            object=self.object,
            minute=self.minute,
            hour=self.hour,
            day=self.day,
            sleep=self.sleep
        )

    def tearDown(self):
        pass

    def test_run(self):
        self.scheduler.run()
        self.assertIsNotNone(self.scheduler)


if __name__ == "main":
    unittest.main()
