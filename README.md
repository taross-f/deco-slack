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