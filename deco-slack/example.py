from deco_slack import deco_slack


@deco_slack(
    start={
        "text": "start text",
        "title": 'start',
        "color": "good"
    },
    success={
        "text": "success text",
        "title": 'success',
        "color": "good"
    },
    error={
        "title": 'error',
        "color": "danger",
        "stacktrace": True
    },
)
def test1():
  print('test1')


@deco_slack(
    start={
        "text": "start text",
        "title": 'start',
        "color": "good"
    },
    success={
        "text": "success text",
        "title": 'success',
        "color": "good"
    },
    error={
        "title": 'error',
        "color": "danger",
        "stacktrace": True
    },
)
def test2():
  raise ValueError('error occured.')


if __name__ == '__main__':
  test1()
  test2()
