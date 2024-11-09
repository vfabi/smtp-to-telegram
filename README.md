# smtp-to-telegram

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/vfabi/smtp-to-telegram)
![GitHub last commit](https://img.shields.io/github/last-commit/vfabi/smtp-to-telegram)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Generic badge](https://img.shields.io/badge/hub.docker.com-vfabi/smtp_to_telegram-<>.svg)](https://hub.docker.com/repository/docker/vfabi/smtp-to-telegram)
![Docker Pulls](https://img.shields.io/docker/pulls/vfabi/smtp-to-telegram)

Is a small program which listens for SMTP (no auth, no ssl) and sends all incoming email messages to Telegram.

## Status

Beta

## Features

- receive (SMTP) and transfer/transform email messages to Telegram
- route email messages to Telegram chats/users specified as email recipients (`chat_id`@telegram.org)
- telegram message template with HTML parsing (`parse_mode='HTML'`)
- telegram chat/user to severity mapping (env `TELEGRAM_RECIPIENT_SEVERITY_MAPPING`)

## Technology stack

- Python 3.12.3+

## Configuration

### Environment variables

Name | Description | Mandatory | Default | Example
--- | --- | --- | --- | ---
SMTP_HOST  | SMTP server host ip address bind to. | false | 0.0.0.0 | `192.168.0.1` |
SMTP_PORT | SMTP server port bind to. | false | 25 | `2525` |
TELEGRAM_TOKEN | Telegram bot token. | true | | `1234567890:AABs9kmnpyEn21ylaOJ4RhXhAaaaBbbbCccc` |
TELEGRAM_MESSAGE_TEMPLATE | Telegram message template. Supported variables: $mail_from,$mail_to,$mail_subject,$mail_body,$mail_dt,$severity | false | `<b>From:</b> $mail_from\n<b>To:</b> $mail_to\n<b>Subject:</b> $mail_subject\n<b>Message:</b> $mail_body\n<b>Datetime:</b> $mail_dt` | |
TELEGRAM_RECIPIENT_SEVERITY_MAPPING | Telegram recipients to severity mapping. Supported severity: NOTICE,DEBUG,INFO,WARNING,ERROR,CRITICAL.| false | | `-1230123123:WARNING,1230456789:INFO` |
APP_NAME | Used for logging only. | false | Takes from docker image environment args or `smtp-to-telegram`. | |
APP_VERSION | Used for logging only. | false | Takes from docker image environment args or `unknown`. | `2.0.0` |
APP_ENVIRONMENT | Used for logging only. | false | `unknown` | `staging` |
APP_LOGGING_TELEGRAM_BOT_TOKEN | Telegram bot token to send logging messages to telegram. Used for logging only. | false | | `1234567890:AABs9kmnpyEn21ylaOJ4RhXhAaaaBbbbCccc` |
APP_LOGGING_TELEGRAM_CHAT_ID_INFO | Telegram bot chat id to send INFO severity log messages. Used for logging only. | false | | `-1230123123` |
APP_LOGGING_TELEGRAM_CHAT_ID_WARNING | Telegram bot chat id to send WARNING severity log messages.  Used for logging only. | false | | `-9876543219` |
APP_LOGGING_TELEGRAM_CHAT_ID_CRITICAL | Telegram bot chat id to send CRITICAL severity log messages.  Used for logging only. | false | | `-1122334455` |

## Usage

### Deployment

For kubernetes environment just apply all yaml files from `deployment/kubernetes/` folder. This is just a working example.

## Docker

[![Generic badge](https://img.shields.io/badge/hub.docker.com-vfabi/smtp_to_telegram-<>.svg)](https://hub.docker.com/repository/docker/vfabi/smtp-to-telegram)

## Contributing

Please refer to each project's style and contribution guidelines for submitting patches and additions. In general, we follow the "fork-and-pull" Git workflow.

 1. **Fork** the repo on GitHub
 2. **Clone** the project to your own machine
 3. **Commit** changes to your own branch
 4. **Push** your work back up to your fork
 5. Submit a **Pull request** so that we can review your changes

NOTE: Be sure to merge the latest from "upstream" before making a pull request!

## License

Apache 2.0
