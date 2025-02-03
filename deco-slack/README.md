# decoslack

decoslack notifies you via Slack if a method has completed successfully or not.

## Description

- Notify Slack when a process starts, ends normally, or ends abnormally.
- Each notification can be set on or off.
- Support dynamic message formatting based on function results or errors.

## Configurations
Environment variables to set
- {DECO_SLACK_PREFIX}SLACK_TOKEN
  - Slack bot token that can be used with chat:write.public scope.
- {DECO_SLACK_PREFIX}SLACK_CHANNEL
  - Channel name to be notified without # (like notify_xxx not #notify_xxx)
- DECO_SLACK_PREFIX (optional)
  - Prefix for environment variables.
    - If not set, defaults to "".
    
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


# Dynamic message formatting example
@deco_slack(
    success={
        "text_formatter": lambda result: f"Process completed with result: {result}",
        "title": "Success",
        "color": "good"
    },
    error={
        "text_formatter": lambda e: f"Error occurred: {str(e)}",
        "title": "Error",
        "color": "danger",
        "stacktrace": True
    }
)
def process_data(data):
    result = data * 2
    return result

```

## Advanced Features

### Dynamic Message Formatting

You can customize notification messages based on function results or errors using `text_formatter` and `title_formatter`:

```python
@deco_slack(
    success={
        "text_formatter": lambda result: f"Process completed with result: {result}",
        "title_formatter": lambda result: f"Success: {result}",
        "color": "good"
    },
    error={
        "text_formatter": lambda e: f"Error details: {str(e)}",
        "color": "danger"
    }
)
def your_function():
    # Your code here
    pass
```

The formatters receive:
- `success`: The function's return value
- `error`: The exception object

This allows you to create more informative and context-aware notifications.
