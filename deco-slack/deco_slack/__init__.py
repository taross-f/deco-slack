from typing import Callable, Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from functools import wraps
import os
import sys
import traceback


__version__ = "0.0.2"


class _Helper:
    client: WebClient
    channel: str

    def __init__(self):
        self._prefix = os.getenv("DECO_SLACK_PREFIX", "")
        token = os.getenv(f"{self._prefix}SLACK_TOKEN")
        self.client = WebClient(token)
        self.channel = os.getenv(f"{self._prefix}SLACK_CHANNEL", "")

        if not (token and self.channel):
            sys.stderr.write(f"deco_slack needs SLACK_TOKEN and SLACK_CHANNEL env.\n")

    def send_attachment(self, attachment: dict):
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=attachment.get("text"),
                attachments=[attachment],
            )
        except SlackApiError as e:
            sys.stderr.write(f"SlackApiError raised. {e}")


class _Printer:
    def send_attachment(self, attachment):
        if "text" in attachment and attachment["text"] is not None:
            print(attachment["text"])
        if "title" in attachment and attachment["title"] is not None:
            print(attachment["title"], attachment["color"])


def _call_func_if_set(attachment, *args):
    if "func" in attachment:
        attachment["func"](*args)


def _create_message(base_message: dict, result: Any = None) -> dict:
    """Create a new message for Slack, applying formatters if they exist"""
    message = {
        "color": base_message.get("color"),
        "title": base_message.get("title"),
        "text": base_message.get("text"),
    }

    # Apply formatters if they exist
    if callable(base_message.get("text_formatter")):
        message["text"] = base_message["text_formatter"](result)
    if callable(base_message.get("title_formatter")):
        message["title"] = base_message["title_formatter"](result)

    # Copy other fields except formatters
    for key, value in base_message.items():
        if key not in ["text_formatter", "title_formatter"] and key not in message:
            message[key] = value

    return message


def deco_slack(**kwargs):
    """
    param sample:
        {
          (start|success|error)={
            'fallback': "",
            "text": "",
            "text_formatter": Callable[[Any], str],  # Optional function to format text based on result
            "title": 'Task A has succeeded :mute:',
            "title_formatter": Callable[[Any], str],  # Optional function to format title based on result
            "title_link": 'http://toaru.url'
            "color": "danger",
            "attachment_type": "default",
            "starcktrace": False
          },
        }
    """
    client = _Printer() if "mocking" in kwargs and kwargs["mocking"] else _Helper()

    def dec(func: Callable):
        @wraps(func)
        def wrapper(*args, **options):
            try:
                if "start" in kwargs:
                    message = _create_message(kwargs["start"])
                    _call_func_if_set(message, *args)
                    client.send_attachment(message)

                result = func(*args, **options)

                if "success" in kwargs:
                    message = _create_message(kwargs["success"], result)
                    _call_func_if_set(message, *args)
                    client.send_attachment(message)

                return result
            except Exception as e:
                if "error" in kwargs:
                    message = _create_message(kwargs["error"], e)
                    if "stacktrace" in kwargs["error"]:
                        message["text"] = (message.get("text", "") +
                                         f"\n```{traceback.format_exc()}```")
                    _call_func_if_set(message, *args)
                    client.send_attachment(message)
                raise

        return wrapper

    return dec
