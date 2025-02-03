import os
from deco_slack import __version__, deco_slack, _Helper


def test_version():
    assert __version__ == "0.0.2"


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
    assert (
        stdout
        == "self.initial=1\nstart good\n_run_with_func()\nself.success=1\nsuccess good\nself.initial=2\nstart good\n_run_with_func()\nself.success=2\nsuccess good\n"
    )
    assert stderr == ""


def test_helper():
    os.environ["SLACK_TOKEN"] = "token"
    os.environ["SLACK_CHANNEL"] = "channel"
    h = _Helper()
    assert h._prefix == ""
    assert h.client.token == "token"
    assert h.channel == "channel"


def test_helper_with_prefix():
    os.environ["DECO_SLACK_SLACK_TOKEN"] = "token"
    os.environ["DECO_SLACK_SLACK_CHANNEL"] = "channel"
    os.environ["DECO_SLACK_PREFIX"] = "DECO_SLACK_"
    h = _Helper()
    assert h._prefix == "DECO_SLACK_"
    assert h.client.token == "token"
    assert h.channel == "channel"


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
        assert False, "Should raise ValueError"
    except ValueError:
        stdout, stderr = capfd.readouterr()
        assert "Failed: ValueError" in stdout
        assert stderr == ""
