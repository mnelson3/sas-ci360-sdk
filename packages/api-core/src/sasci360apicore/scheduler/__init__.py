#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
import time

from schedule import ScheduleError, every, run_pending


class Scheduler:
	"""
	Loren ipsum
	"""

	def __init__(self, **kwargs) -> None:
		"""

		:keyword object:
		:keyword minute: int
		:keyword hour: int
		:keyword day: str
		:keyword sleep: int

		"""
		self.logger = logging.getLogger(__name__)

		self.object = kwargs["object"]
		self.minute = kwargs["minute"]
		self.hour = kwargs["hour"]
		self.day = kwargs["day"]
		self.sleep = kwargs["sleep"]

	def run(self) -> None:
		"""

		"""
		sleep_seconds = self.sleep
		schedule_job = self.object
		minute = self.minute
		hour = self.hour
		day = self.day
		program_time = "{0}:{1}".format(hour, minute)

		try:
			if day == "monday":
				every().monday.at(program_time).do(job_func=schedule_job)
			elif day == "tuesday":
				every().tuesday.at(program_time).do(job_func=schedule_job)
			elif day == "wednesday":
				every().wednesday.at(program_time).do(job_func=schedule_job)
			elif day == "thursday":
				every().thursday.at(program_time).do(job_func=schedule_job)
			elif day == "friday":
				every().friday.at(program_time).do(job_func=schedule_job)
			elif day == "saturday":
				every().saturday.at(program_time).do(job_func=schedule_job)
			elif day == "sunday":
				every().sunday.at(program_time).do(job_func=schedule_job)
			else:
				every().day.at(program_time).do(job_func=schedule_job)
		except (ScheduleError, TypeError) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
			return

		while True:
			try:
				run_pending()
			except Exception as e:
				# Broad on purpose: schedule_job is caller-supplied and can fail in
				# arbitrary ways. One bad run must not take the whole scheduler down.
				self.logger.exception("Exception occurred: {}".format(str(e)))
			time.sleep(sleep_seconds)


if __name__ == "__main__":
	Scheduler()
