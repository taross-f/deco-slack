import os
import unittest.mock
from typing import List, Dict

from deco_slack import (
    __version__, 
    ConsoleHandler, 
    NotificationHandler, 
    SlackHandler, 
    _Helper, 
    deco_slack
)


def test_version():
    assert __version__ == "0.0.2"


class MockHandler(NotificationHandler):
    """Custom notification handler for testing."""
    
    def __init__(self):
        self.messages: List[Dict] = []
    
    def send_attachment(self, attachment: dict) -> None:
        """Record message in message log."""
        self.messages.append(attachment.copy())


@deco_slack(
    start={"title": "start", "color": "good"},
    success={"title": "success", "color": "good"},
    error={"title": "error", "color": "danger", "stacktrace": True},
    mocking=True,
)
def _run_success():
    print("_run_success()")


def test_success(capfd):
    _run_success()
    stdout, stderr = capfd.readouterr()
    assert stdout == "start good\n_run_success()\nsuccess good\n"
    assert stderr == ""


class FuncTest:
    def __init__(self):
        self.initial = 1
        self.success = 0

    def _start(self):
        print(f"{self.initial=}")

    def _success(self):
        print(f"{self.success=}")

    @deco_slack(
        start={"title": "start", "color": "good", "func": _start},
        success={"title": "success", "color": "good", "func": _success},
        error={"title": "error", "color": "danger", "stacktrace": True},
        mocking=True,
    )
    def _run_with_func(self):
        self.initial += 1
        print("_run_with_func()")
        self.success += 1


def test_success_with_func(capfd):
    obj = FuncTest()
    obj._run_with_func()
    obj._run_with_func()
    stdout, stderr = capfd.readouterr()
    print(stdout)
    expected = (
        "self.initial=1\n"
        "start good\n"
        "_run_with_func()\n"
        "self.success=1\n"
        "success good\n"
        "self.initial=2\n"
        "start good\n"
        "_run_with_func()\n"
        "self.success=2\n"
        "success good\n"
    )
    assert stdout == expected
    assert stderr == ""


def test_slack_handler():
    os.environ["SLACK_TOKEN"] = "token"
    os.environ["SLACK_CHANNEL"] = "channel"
    h = SlackHandler()
    assert h._prefix == ""
    assert h.token == "token"
    assert h.client.token == "token"
    assert h.channel == "channel"


def test_slack_handler_with_prefix():
    os.environ["DECO_SLACK_SLACK_TOKEN"] = "token"
    os.environ["DECO_SLACK_SLACK_CHANNEL"] = "channel"
    os.environ["DECO_SLACK_PREFIX"] = "DECO_SLACK_"
    h = SlackHandler()
    assert h._prefix == "DECO_SLACK_"
    assert h.token == "token"
    assert h.client.token == "token"
    assert h.channel == "channel"


def test_slack_handler_with_direct_parameters():
    h = SlackHandler(token="direct_token", channel="direct_channel", prefix="direct_prefix_")
    assert h._prefix == "direct_prefix_"
    assert h.token == "direct_token"
    assert h.channel == "direct_channel"


def test_helper_backwards_compatibility():
    """Test that the _Helper alias still works correctly."""
    os.environ["SLACK_TOKEN"] = "token"
    os.environ["SLACK_CHANNEL"] = "channel"
    if "DECO_SLACK_PREFIX" in os.environ:
        del os.environ["DECO_SLACK_PREFIX"]
    h = _Helper()
    assert h._prefix == ""
    assert h.token == "token"
    assert h.client.token == "token"
    assert h.channel == "channel"


# Test with custom handler injection
def test_custom_handler_injection():
    """Test using a custom handler injected directly."""
    mock_handler = MockHandler()
    
    @deco_slack(
        start={"title": "Start Test", "color": "good"},
        success={"title": "Success Test", "color": "good"},
        handler=mock_handler
    )
    def test_function():
        return "result"
    
    # Run decorated function
    result = test_function()
    
    # Verify results
    assert result == "result"
    assert len(mock_handler.messages) == 2
    assert mock_handler.messages[0]["title"] == "Start Test"
    assert mock_handler.messages[1]["title"] == "Success Test"


# 動的メッセージフォーマットのテスト
@deco_slack(
    success={
        "text_formatter": lambda result: f"Result: {result}",
        "title_formatter": lambda result: f"Success: {result}",
        "color": "good",
    },
    error={
        "text_formatter": lambda e: f"Error: {str(e)}",
        "title_formatter": lambda e: f"Failed: {type(e).__name__}",
        "color": "danger",
    },
    mocking=True,
)
def _process_with_formatters(success: bool = True):
    if success:
        return "test_value"
    raise ValueError("test_error")


def test_dynamic_formatting_success(capfd):
    result = _process_with_formatters(True)
    stdout, stderr = capfd.readouterr()
    assert result == "test_value"
    assert "Success: test_value" in stdout
    assert stderr == ""


def test_dynamic_formatting_error(capfd):
    try:
        _process_with_formatters(False)
        raise AssertionError("Should raise ValueError")
    except ValueError:
        stdout, stderr = capfd.readouterr()
        assert "Failed: ValueError" in stdout
        assert stderr == ""


def test_console_handler():
    """Test that ConsoleHandler properly stores messages."""
    handler = ConsoleHandler()
    handler.send_attachment({"title": "Test Title", "color": "good", "text": "Test Text"})
    
    assert len(handler.messages) == 1
    assert handler.messages[0]["title"] == "Test Title"
    assert handler.messages[0]["color"] == "good"
    assert handler.messages[0]["text"] == "Test Text"
