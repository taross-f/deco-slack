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
        if "text" in attachment:
            print(attachment["text"])
        print(attachment["title"], attachment["color"])


def _call_func_if_set(attachment, *args):
    if "func" in attachment:
        attachment["func"](*args)


def _update_message(message: dict, result: Any) -> dict:
    """Update message with function result"""
    if callable(message.get("text_formatter")):
        message["text"] = message["text_formatter"](result)
    if callable(message.get("title_formatter")):
        message["title"] = message["title_formatter"](result)
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
                    _call_func_if_set(kwargs["start"], *args)
                    client.send_attachment(kwargs["start"].copy())

                result = func(*args, **options)

                if "success" in kwargs:
                    success_message = kwargs["success"].copy()
                    success_message = _update_message(success_message, result)
                    _call_func_if_set(success_message, *args)
                    client.send_attachment(success_message)

                return result
            except Exception as e:
                if "error" in kwargs:
                    error_message = kwargs["error"].copy()
                    error_message["text"] = error_message.get("text", "")
                    if "stacktrace" in error_message:
                        error_message["text"] += f"\n```{traceback.format_exc()}```"
                    error_message = _update_message(error_message, e)
                    _call_func_if_set(error_message, *args)
                    client.send_attachment(error_message)
                raise

        return wrapper

    return dec
