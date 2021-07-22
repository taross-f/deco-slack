# decoslack

decoslack notifies you if a method has completed successfully or not.

## Description

- Notify Slack when a process starts, ends normally, or ends abnormally.
- Each notification can be set on or off.

## Configurations
Environment variables to set
- SLACK_TOKEN
  - Slack bot token that can be used with chat:write.public scope.
- SLACK_CHANNEL
  - Channel name to be notified without # (like notify_xxx not #notify_xxx)

## Example

```py
from deco_slack import deco_slack


@deco_slack(
    # These parameters are all optional
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
        "stacktrace": True # Set True if you need stacktrace in a notification
    },
)
def test1():
  print('test1')


@deco_slack(
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
def error1():
  raise ValueError('error occured.')

```

