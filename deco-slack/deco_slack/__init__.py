from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from functools import wraps
import os
import sys
import traceback


__version__ = '0.0.1'


class _Helper:
  def __init__(self):
    if not (os.getenv('SLACK_TOKEN') and os.getenv('SLACK_CHANNEL')):
      sys.stderr.write(f'deco_slack needs SLACK_TOKEN and SLACK_CHANNEL env.\n')

    self.client = WebClient(os.getenv('SLACK_TOKEN'))
    self.channel = os.getenv('SLACK_CHANNEL')

  def send_attachment(self, attachment):
    try:
      self.client.chat_postMessage(
          channel=self.channel,
          text=attachment.get('text'),
          attachments=[attachment]
      )
    except SlackApiError as e:
      sys.stderr.write(f'SlackApiError raised. {e}')


class _Printer:
  def send_attachment(self, attachment):
    print(attachment["title"], attachment["color"])


def _call_func_if_set(attachment, *args):
  if 'func' in attachment:
    attachment['func'](*args)


def deco_slack(**kwargs):
  '''
  param sample:
      {
        (start|success|error)={
          'fallback': "",
          "text": "",
          "title": 'Task A has succeeded :mute:',
          "title_link": 'http://toaru.url'
          "color": "danger",
          "attachment_type": "default",
          "starcktrace": False
        },
      }
  '''
  client = _Printer() if 'mocking' in kwargs and kwargs['mocking'] else _Helper()

  def dec(func):
    @wraps(func)
    def wrapper(*args, **options):
      try:
        if 'start' in kwargs:
          _call_func_if_set(kwargs['start'], *args)
          client.send_attachment(
              kwargs['start']
          )
        func(*args, **options)

        if 'success' in kwargs:
          _call_func_if_set(kwargs['success'], *args)
          client.send_attachment(
              kwargs['success']
          )
      except:
        if 'error' in kwargs:
          attachment = kwargs['error']
          attachment['text'] = attachment['text'] if 'text' in attachment else ''
          if 'stacktrace' in attachment:
            attachment['text'] += f"\n```{traceback.format_exc()}```"
          _call_func_if_set(kwargs['error'], *args)
          client.send_attachment(
              attachment
          )
        raise
    return wrapper
  return dec
