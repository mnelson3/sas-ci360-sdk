#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import unittest
from datetime import datetime
from pathlib import Path
from sasci360apicore import communication


class TestCommunication(unittest.TestCase):

	def setUp(self):
		self.log_file_path = "logs/communication.log"
		self.email_server = "smtp.example.com"
		self.email_server_login = "example.sender@example.com"
		self.email_server_password = "example-password"
		self.email_server_port = 465

		self.email_msg_from = "example.sender@example.com"
		self.email_msg_to = "example.recipient@example.com"
		self.email_msg_cc = "example.recipient@example.com"
		self.email_msg_bcc = "example.recipient@example.com"
		self.email_msg_subject = None
		self.email_msg_body = None
		self.email_msg_attachment = None

		self.communication = communication.Communication(
			email_server=self.email_server,
			email_server_login=self.email_server_login,
			email_server_port=self.email_server_port,
			email_server_password=self.email_server_password
		)

	def tearDown(self):
		pass

	def test_communication_msg_settings(self):
		email_msg_from = self.email_msg_from
		email_msg_to = self.email_msg_to
		email_msg_cc = self.email_msg_cc
		email_msg_bcc = self.email_msg_bcc
		email_msg_subject = self.email_msg_subject
		email_msg_body = self.email_msg_body
		email_msg_attachment = self.email_msg_attachment

		self.assertEqual(email_msg_from, "example.sender@example.com")
		self.assertEqual(email_msg_to, "example.recipient@example.com")
		self.assertEqual(email_msg_cc, "example.recipient@example.com")
		self.assertEqual(email_msg_bcc, "example.recipient@example.com")
		self.assertIsNone(email_msg_subject)
		self.assertIsNone(email_msg_body)
		self.assertIsNone(email_msg_attachment)

	def test_communication_send_status_message(self):
		time_stamp = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
		time_stamp_ = "20200519120935"

		email_msg_from = self.email_msg_from
		email_msg_to = self.email_msg_to
		email_msg_cc = self.email_msg_cc
		email_msg_bcc = self.email_msg_bcc
		# email_msg_subject = self.email_msg_subject
		# email_msg_body = self.email_msg_body
		# email_msg_attachment = self.email_msg_attachment

		root_folder = "tests"
		output_folder = "/output"
		file_name = "import_request_jobs_get_{}".format(time_stamp_)
		csv_file = Path("{0}{1}{2}{3}".format(root_folder, output_folder, file_name, ".CSV"))

		email_msg_from = "SAS CI360 API Core [DO-NOT-REPLY] <{}>".format(email_msg_from)
		email_msg_subject = "Daily Identity Bridge Update [{0}]".format(time_stamp)
		email_msg_body = ""
		email_msg_attachment = csv_file

		self.communication.send_email(
			email_msg_from=email_msg_from,
			email_msg_to=email_msg_to,
			email_msg_cc=email_msg_cc,
			email_msg_bcc=email_msg_bcc,
			email_msg_subject=email_msg_subject,
			email_msg_body=email_msg_body,
			email_msg_attachment=email_msg_attachment
		)
		# self.assertIsNone(result)

	def test_communication_send_support_message(self):
		time_stamp = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
		time_stamp_ = "20200519120935"

		email_msg_from = self.email_msg_from
		email_msg_to = self.email_msg_to
		email_msg_cc = self.email_msg_cc
		# email_msg_bcc = self.email_msg_bcc
		# email_msg_subject = self.email_msg_subject
		# email_msg_body = self.email_msg_body
		# email_msg_attachment = self.email_msg_attachment

		tenant_environment = "example_environment"
		tenant_name = "Example Production Tenant"
		tenant_number = "0000000"
		tenant_product = "SAS Customer Intelligence 360"
		tenant_url = "https://platform-use.ci360.sas.com/SASCustomerIntelligenceHome/"

		root_folder = "tests"
		output_folder = "/output"
		file_name = "example_change_{}".format(time_stamp_)
		csv_file = Path("{0}{1}{2}{3}".format(root_folder, output_folder, file_name, ".CSV"))

		email_msg_from = "SAS CI360 API Core [DO-NOT-REPLY] <{}>".format(email_msg_from)
		email_msg_subject = "Identity Bridge Change Update [{0}]".format(time_stamp)
		email_msg_body = "Environment: {0}\n" \
		                 "Name: {1}\n" \
		                 "Number: {2}\n" \
		                 "Product: {3}\n" \
		                 "URL: {4}\n" \
		                 "User: {5}\n" \
		                 "Time of attempt: {6}\n" \
		                 "Issue:".format(tenant_environment, tenant_name, tenant_number, tenant_product, tenant_url, email_msg_from, time_stamp)
		email_msg_attachment = csv_file

		self.communication.send_email(
			email_msg_from=email_msg_from,
			email_msg_to=email_msg_to,
			email_msg_cc=email_msg_cc,
			email_msg_subject=email_msg_subject,
			email_msg_body=email_msg_body,
			email_msg_attachment=email_msg_attachment
		)
		# self.assertIsNone(result)


if __name__ == "main":
	unittest.main()
