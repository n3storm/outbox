'''
File: outbox.py
Author: Nathan Hoad
Description: Simple wrapper around smtplib for sending an email
'''

import os
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

class Email(object):
    def __init__(self, recipients, subject, body):
        if not recipients:
            raise ValueError("At least one recipient must be specified!")

        iter(recipients)

        for r in recipients:
            if not isinstance(r, basestring):
                raise TypeError("Recipient not a string: %s" % r)

        self.recipients = recipients
        self.subject = subject
        self.body = body


class Attachment(object):
    def __init__(self, name, filepath=None, raw=None):
        if filepath and raw:
            raise ValueError("filepath and raw can't both be set.")

        if not filepath and raw is None:
            raise ValueError("one of filepath or raw must be set.")

        if filepath and not os.path.isfile(filepath):
            raise OSError("File does not exist: %s" % filepath)

        self.name = name
        self.filepath = filepath
        self.raw = raw

    def read(self):
        if self.raw:
            return self.raw

        with open(self.filepath) as f:
            return f.read()

class Outbox(object):
    def __init__(self, username, password, server, port, use_tls=True):
        self.username = username
        self.password = password
        self.connection_details = (server, port, use_tls)

    def _login(self):
        server, port, secure = self.connection_details

        smtp = smtplib.SMTP(server, port)

        if secure:
            smtp.starttls()

        smtp.login(self.username, self.password)
        return smtp

    def send(self, email, attachments=()):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(email.recipients)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = email.subject

        msg.attach(MIMEText(email.body))

        for f in attachments:
            if not isinstance(f, Attachment):
                raise TypeError("attachment must be of type Attachment")
            add_attachment(msg, f)

        smtp = self._login()
        smtp.sendmail(self.username, email.recipients, msg.as_string())

def add_attachment(message, attachment):
    data = attachment.read()
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(attachment.name)))

    message.attach(part)
