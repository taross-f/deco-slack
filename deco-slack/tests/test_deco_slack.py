from deco_slack import __version__
from deco_slack.deco_slack import deco_slack


def test_version():
  assert __version__ == '0.1.0'

@deco_slack(
    start={
        "title": 'start',
        "color": "good"
    },
    success={
        "title": 'success',
        "color": "good"
    },
    error={
        "title": 'error',
        "color": "danger",
        "stacktrace": True
    },
    mocking=True
)
def _run_success():
  print('_run_success()')

def test_success(capfd):
  _run_success()
  stdout, stderr = capfd.readouterr()
  assert stdout == "None start good\n_run_success()\nNone success good\n"
  assert stderr == ""

class FuncTest():
  def __init__(self):
    self.initial = 1
    self.success = 0

  def _start(self):
    print(f'{self.initial=}')

  def _success(self):
    print(f'{self.success=}')

  @deco_slack(
      start={
          "title": 'start',
          "color": "good",
          "func": _start
      },
      success={
          "title": 'success',
          "color": "good",
          "func": _success
      },
      error={
          "title": 'error',
          "color": "danger",
          "stacktrace": True
      },
      mocking=True
  )
  def _run_with_func(self):
    self.initial += 1
    print('_run_with_func()')
    self.success += 1

def test_success_with_func(capfd):
  obj = FuncTest()
  obj._run_with_func()
  obj._run_with_func()
  stdout, stderr = capfd.readouterr()
  print(stdout)
  assert stdout == "self.initial=1\nNone start good\n_run_with_func()\nself.success=1\nNone success good\nself.initial=2\nNone start good\n_run_with_func()\nself.success=2\nNone success good\n"
  assert stderr == ""
