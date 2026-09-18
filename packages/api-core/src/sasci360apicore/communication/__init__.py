#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Communication:
	"""
	Communication Module
	Contains operations to send emails
		1. 	def send_email(self, **kwargs) -> None
	"""

	def __init__(self, **kwargs) -> None:
		"""

		:keyword email_server:
		:keyword email_server_login:
		:keyword email_server_password:
		:keyword email_server_port:

		"""
		self.logger = logging.getLogger(__name__)

		self.email_server = kwargs["email_server"]
		self.email_server_login = kwargs["email_server_login"]
		self.email_server_password = kwargs["email_server_password"]
		self.email_server_port = kwargs["email_server_port"]

	def send_email(self, **kwargs) -> None:
		"""

		:keyword email_msg_from:
		:keyword email_msg_to:
		:keyword email_msg_cc:
		:keyword email_msg_bcc:
		:keyword email_msg_subject:
		:keyword email_msg_body:
		:keyword email_msg_attachment:


		"""
		host = self.email_server
		port = self.email_server_port
		login = self.email_server_login
		password = self.email_server_password

		email_msg_from = None
		email_msg_to = None
		email_msg_cc = None
		email_msg_bcc = None
		email_msg_subject = None
		email_msg_body = None
		email_msg_attachment = None
		try:
			if "email_msg_from" in kwargs:
				email_msg_from = kwargs["email_msg_from"]
			if "email_msg_to" in kwargs:
				email_msg_to = kwargs["email_msg_to"]
			if "email_msg_cc" in kwargs:
				email_msg_cc = kwargs["email_msg_cc"]
			if "email_msg_bcc" in kwargs:
				email_msg_bcc = kwargs["email_msg_bcc"]
			if "email_msg_subject" in kwargs:
				email_msg_subject = kwargs["email_msg_subject"]
			if "email_msg_body" in kwargs:
				email_msg_body = kwargs["email_msg_body"]
			if "email_msg_attachment" in kwargs:
				email_msg_attachment = kwargs["email_msg_attachment"]

			message = MIMEMultipart()
			message["From"] = email_msg_from
			message["To"] = email_msg_to
			message["CC"] = email_msg_cc
			message["BCC"] = email_msg_bcc
			message["Subject"] = email_msg_subject

			# Add body to email
			message.attach(MIMEText(email_msg_body, "plain"))

			if email_msg_attachment is not None:
				filename = email_msg_attachment

				# Open PDF file in binary mode
				with open(filename, "rb") as attachment:
					# Add file as application/octet-stream
					# Email client can usually download this automatically as attachment
					part = MIMEBase("application", "octet-stream")
					part.set_payload(attachment.read())

				# Encode file in ASCII characters to send by email
				encoders.encode_base64(part)

				# Add header as key/value pair to attachment part
				part.add_header("Content-Disposition", f"attachment; filename= {filename}", )

				# Add attachment to message and convert message to string
				message.attach(part)

			text = message.as_string()
			context = ssl.create_default_context()
			with smtplib.SMTP_SSL(host=host, port=port, context=context) as server:
				server.login(login, password)
				server.sendmail(email_msg_from, email_msg_to, text)
			server.close()
		except (AttributeError, Exception) as e:
			self.logger.exception("Exception occurred: {}".format(str(e)))
		finally:
			return


if __name__ == "__main__":
	Communication()
