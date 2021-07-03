__version__ = '0.0.1'

from slack_sdk import WebClient
import os
import traceback


class SlackClient:
  def __init__(self):
    self.client = WebClient(os.getenv('SLACK_TOKEN'))
    self.channel = os.getenv('SLACK_CHANNEL')

  def send_attachment(self, title, attachment):
    self.client.chat_postMessage(
        channel=self.channel,
        text=title,
        attachments=[attachment]
    )


class PrintClient:
  def send_attachment(self, title, attachment):
    print(title, attachment["title"], attachment["color"])


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
  client = PrintClient() if 'mocking' in kwargs and kwargs['mocking'] else SlackClient()

  def dec(func):
    def wrapper(*args, **options):
      try:
        if 'start' in kwargs:
          _call_func_if_set(kwargs['start'], *args)
          client.send_attachment(
              None,
              kwargs['start']
          )
        func(*args, **options)

        if 'success' in kwargs:
          _call_func_if_set(kwargs['success'], *args)
          client.send_attachment(
              None,
              kwargs['success']
          )
      except Exception as e:
        if 'error' in kwargs:
          attachment = kwargs['error']
          attachment['text'] = attachment['text'] if 'text' in attachment else ''
          if 'stacktrace' in attachment:
            attachment['text'] += f"\n```{traceback.format_exc()}```"
          _call_func_if_set(kwargs['error'], *args)
          client.send_attachment(
              None,
              attachment
          )
        raise
    return wrapper
  return dec
