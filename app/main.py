#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Project: smtp-to-telegram
    Description: program which listens for SMTP and sends all incoming Email messages to Telegram.
    Initial date: 2024-11-08
    License: this file is subject to the terms and conditions defined
        in file 'LICENSE.txt', which is part of this source code package
    Copyright: © 2024 by vfabi
    Author: vfabi
    Support: vfabi
    Todo:
"""

import os
import string
import threading
import email
from email.utils import parseaddr, getaddresses
import requests
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from python_app_logger import get_logger


APP_NAME = os.getenv('APP_NAME', 'smtp-to-telegram')
APP_VERSION = os.getenv('APP_VERSION', 'unknown')
APP_ENVIRONMENT = os.getenv('APP_ENVIRONMENT', 'unknown')
APP_LOGGING_TELEGRAM_BOT_TOKEN = os.getenv('APP_LOGGING_TELEGRAM_BOT_TOKEN')
APP_LOGGING_TELEGRAM_CHAT_ID_INFO = os.getenv('APP_LOGGING_TELEGRAM_CHAT_ID_INFO')
APP_LOGGING_TELEGRAM_CHAT_ID_WARNING = os.getenv('APP_LOGGING_TELEGRAM_CHAT_ID_WARNING')
APP_LOGGING_TELEGRAM_CHAT_ID_CRITICAL = os.getenv('APP_LOGGING_TELEGRAM_CHAT_ID_CRITICAL')
SMTP_HOST = os.getenv('SMTP_HOST', '0.0.0.0')
SMTP_PORT = os.getenv('SMTP_PORT', '25')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_MESSAGE_TEMPLATE = os.getenv('TELEGRAM_MESSAGE_TEMPLATE', '<b>From:</b> $mail_from\n<b>To:</b> $mail_to\n<b>Subject:</b> $mail_subject\n<b>Message:</b> $mail_body\n<b>Datetime:</b> $mail_dt')
TELEGRAM_RECIPIENT_SEVERITY_MAPPING = os.getenv('TELEGRAM_RECIPIENT_SEVERITY_MAPPING')
TELEGRAM_RECIPIENT_SEVERITY_MAPPING_DICT = None
if TELEGRAM_RECIPIENT_SEVERITY_MAPPING:
    TELEGRAM_RECIPIENT_SEVERITY_MAPPING_DICT = {key: value for key, value in (pair.split(':') for pair in TELEGRAM_RECIPIENT_SEVERITY_MAPPING .split(','))}
SEVERITY_MAPPING = {
    "NOTICE": "🔵",
    "DEBUG": "⚪",
    "INFO": "🟢",
    "WARNING": "🟠",
    "ERROR": "🔴",
    "CRITICAL": "🔴"
}


logger = get_logger(
    app_name=APP_NAME,
    app_version=APP_VERSION,
    app_environment=APP_ENVIRONMENT,
    telegram_bot_id=APP_LOGGING_TELEGRAM_BOT_TOKEN,
    telegram_chat_ids={
        'critical': APP_LOGGING_TELEGRAM_CHAT_ID_CRITICAL,
        'info': APP_LOGGING_TELEGRAM_CHAT_ID_INFO,
        'warning': APP_LOGGING_TELEGRAM_CHAT_ID_WARNING
    }
)


def send_telegram_message(message, chat_id):
    """Send message to Telegram."""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message.replace('\\n', '\n'),
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=data, timeout=5)
        if response.status_code != 200:
            logger.critical(f'Send message to Telegram was unsuccessful. Telegram response code: {response.status_code}')
        else:
            logger.debug(f'Send message to Telegram was successful, chat_id={chat_id}')
    except requests.exceptions.RequestException as e:
        logger.critical(f'Send message to Telegram general error. Exception: {e}')


def start_smtp_server():
    """Start multithreaded basic SMTP server."""

    logger.info(f'Start multithreaded basic SMTP server at {SMTP_HOST}:{SMTP_PORT}')
    controller = Controller(SMTPHandler(), hostname=SMTP_HOST, port=SMTP_PORT)
    controller.start()

    while True:
        pass


class SMTPHandler(Message):
    """Handle email message to process and send to Telegram."""

    def handle_message(self, message):
        """Process every email message in separate thread."""

        thread = threading.Thread(target=self.process_message, args=(message,))
        thread.start()

    def process_message(self, message):
        """Extract data from email message, transform and send to Telegram.

            Args:
                message(:obj:`Message`): Email message object.
        """

        msg = email.message_from_string(str(message))
        mail_to_addresses = getaddresses(msg.get_all('To', []))
        mail_to_cc_addresses = getaddresses(msg.get_all('Cc', []))
        mail_to_bcc_addresses = getaddresses(msg.get_all('Bcc', []))
        mail_to_all_addresses = list(map(lambda x: x[1], mail_to_addresses + mail_to_cc_addresses + mail_to_bcc_addresses))
        mail_to = ','.join(mail_to_all_addresses)
        mail_subject = message['subject']
        mail_from = parseaddr(message['from'])[1]
        mail_dt = message['date']
        # mail_to = parseaddr(message['to'])[1]

        logger.debug(f"Got new email message from: {mail_from}; to: {mail_to}; subject: {mail_subject}")

        mail_body = self.get_body(message)

        for email_address in set(mail_to_all_addresses):
            recipient_id = email_address.split('@')[0]
            recipient_domain = email_address.split('@')[1]
            if recipient_domain == 'telegram.org':
                if TELEGRAM_RECIPIENT_SEVERITY_MAPPING_DICT:
                    if recipient_id in TELEGRAM_RECIPIENT_SEVERITY_MAPPING_DICT:
                        severity = TELEGRAM_RECIPIENT_SEVERITY_MAPPING_DICT[recipient_id]
                        severity_string = f"{SEVERITY_MAPPING[severity]} <b>{severity}</b>"
                    else:
                        severity = 'NOTICE'
                        severity_string = f"{SEVERITY_MAPPING[severity]} <b>{severity}</b>"
                else:
                    severity = 'NOTICE'
                    severity_string = f"{SEVERITY_MAPPING[severity]} <b>{severity}</b>"
                telegram_message = string.Template(TELEGRAM_MESSAGE_TEMPLATE).substitute(
                    mail_subject=mail_subject,
                    mail_body=mail_body,
                    mail_from=mail_from,
                    mail_to=mail_to,
                    severity=severity_string,
                    mail_dt=mail_dt
                )
                send_telegram_message(telegram_message, recipient_id)
            else:
                logger.debug(f'Email recipient {email_address} domain is not telegram.org, do nothing.')

    def get_body(self, message):
        """Extract email message body (plain text or HTML).

            Args:
                message(:obj:`Message`): Email message object.
            Returns:
                Email message message as string.
        """

        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain" and part.get_content_disposition() != "attachment":
                    return part.get_payload(decode=True).decode()
                if part.get_content_type() == "text/html" and part.get_content_disposition() != "attachment":
                    return part.get_payload(decode=True).decode()
        else:
            return message.get_payload(decode=True).decode()


if __name__ == "__main__":
    start_smtp_server()
