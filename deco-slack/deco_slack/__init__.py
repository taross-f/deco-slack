import os
import sys
import traceback
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

__version__ = "0.0.2"

__all__ = [
    "__version__",
    "NotificationHandler",
    "SlackHandler",
    "ConsoleHandler",
    "_Helper",
    "_Printer",
    "deco_slack",
]


class NotificationHandler(ABC):
    """Abstract base class for notification handlers."""

    @abstractmethod
    def send_attachment(self, attachment: dict) -> None:
        """Send a notification with attachment data."""
        pass


class SlackHandler(NotificationHandler):
    """Handles notifications by sending them to Slack."""

    def __init__(
        self,
        token: Optional[str] = None,
        channel: Optional[str] = None,
        prefix: str = "",
    ):
        """Initialize Slack client with token and channel.

        Args:
            token: Slack API token. If None, read from environment.
            channel: Slack channel ID. If None, read from environment.
            prefix: Environment variable prefix for token and channel.
        """
        self._prefix = prefix or os.getenv("DECO_SLACK_PREFIX", "")
        self.token = token or os.getenv(f"{self._prefix}SLACK_TOKEN")
        self.client = WebClient(self.token)
        self.channel = channel or os.getenv(f"{self._prefix}SLACK_CHANNEL", "")

        if not (self.token and self.channel):
            sys.stderr.write("deco_slack needs SLACK_TOKEN and SLACK_CHANNEL env.\n")

    def send_attachment(self, attachment: dict) -> None:
        """Send attachment to Slack channel.

        Args:
            attachment: Dictionary with message data.
        """
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=attachment.get("text"),
                attachments=[attachment],
            )
        except SlackApiError as e:
            sys.stderr.write(f"SlackApiError raised. {e}")


class ConsoleHandler(NotificationHandler):
    """Handles notifications by printing to console. Useful for testing."""

    def __init__(self):
        """Initialize console handler with empty message log."""
        self.messages: List[Dict] = []

    def send_attachment(self, attachment: dict) -> None:
        """Print attachment to console and store in message log.

        Args:
            attachment: Dictionary with message data.
        """
        self.messages.append(attachment.copy())

        if "text" in attachment and attachment["text"] is not None:
            print(attachment["text"])
        if "title" in attachment and attachment["title"] is not None:
            print(attachment["title"], attachment["color"])


# For backward compatibility
_Helper = SlackHandler
_Printer = ConsoleHandler


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
    """Decorator to send notifications to Slack before/after function execution.

    Args:
        **kwargs: Configuration options including:
            - start: Message to send before function execution.
            - success: Message to send after successful function execution.
            - error: Message to send on exception.
            - mocking: If True, use ConsoleHandler instead of SlackHandler.
            - handler: Custom NotificationHandler instance to use.

    Message format:
        {
          'fallback': "",
          "text": "",
          "text_formatter": Callable[[Any], str],  # Format text
          "title": 'Task A has succeeded :mute:',
          "title_formatter": Callable[[Any], str],  # Format title
          "title_link": 'http://toaru.url'
          "color": "danger",
          "attachment_type": "default",
          "stacktrace": False
        }

    Returns:
        Function decorator.
    """
    # Allow custom handler injection for easier testing
    handler = kwargs.get("handler")
    if handler is None:
        handler = ConsoleHandler() if kwargs.get("mocking") else SlackHandler()

    def dec(func: Callable):
        @wraps(func)
        def wrapper(*args, **options):
            try:
                # Send start message if configured
                if "start" in kwargs:
                    message = _create_message(kwargs["start"])
                    _call_func_if_set(message, *args)
                    handler.send_attachment(message)

                # Execute wrapped function
                result = func(*args, **options)

                # Send success message if configured
                if "success" in kwargs:
                    message = _create_message(kwargs["success"], result)
                    _call_func_if_set(message, *args)
                    handler.send_attachment(message)

                return result
            except Exception as e:
                # Send error message if configured
                if "error" in kwargs:
                    message = _create_message(kwargs["error"], e)
                    # Add stacktrace if configured
                    if kwargs["error"].get("stacktrace"):
                        message["text"] = (
                            message.get("text", "")
                            + f"\n```{traceback.format_exc()}```"
                        )
                    _call_func_if_set(message, *args)
                    handler.send_attachment(message)
                raise

        return wrapper

    return dec
