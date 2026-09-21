#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

import logging
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


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

        email_msg_from: Optional[str] = kwargs.get("email_msg_from")
        email_msg_to: Optional[str] = kwargs.get("email_msg_to")
        email_msg_cc: Optional[str] = kwargs.get("email_msg_cc")
        email_msg_bcc: Optional[str] = kwargs.get("email_msg_bcc")
        email_msg_subject: Optional[str] = kwargs.get("email_msg_subject")
        email_msg_body: Optional[str] = kwargs.get("email_msg_body")
        email_msg_attachment = kwargs.get("email_msg_attachment")
        try:
            message = MIMEMultipart()
            headers = (
                ("From", email_msg_from),
                ("To", email_msg_to),
                ("CC", email_msg_cc),
                ("BCC", email_msg_bcc),
                ("Subject", email_msg_subject),
            )
            for header_name, header_value in headers:
                if header_value is not None:
                    message[header_name] = header_value

            # Add body to email
            message.attach(MIMEText(email_msg_body or "", "plain"))

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
                server.sendmail(email_msg_from or "", email_msg_to or "", text)
            server.close()
        except (smtplib.SMTPException, OSError) as e:
            self.logger.exception("Exception occurred: {}".format(str(e)))


if __name__ == "__main__":
    Communication()
