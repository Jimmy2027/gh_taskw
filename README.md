# Taskwarrior integration for Github notifications

This is a simple python package that integrates Taskwarrior with Github notifications. It uses the Github API to fetch notifications and creates a task for each one of them.

For more information about the gh api, please refer to the [official documentation](https://docs.github.com/en/rest/activity/notifications?apiVersion=2022-11-28#list-notifications-for-the-authenticated-user).

## Installation

## Dependencies

gh_taskw can be configered to use [tasknote](https://github.com/Jimmy2027/TaskNote).
If you choose to use tasknote, you will need to install it and configure it.

### pip

```bash
$ git clone https://github.com/Jimmy2027/gh_taskw.git
$ cd gh_taskw
$ pip install .
```

## Example Configuration

The configuation file is located at `~/.config/gh_taskw.toml`.

```toml
# ~/.config/gh_taskw.toml
tasknote_config = "~/.config/tasknote.toml" # Use tasknote

# ignore notifications from ci runs for example
ignore_notification_reasons = ["ci_activity"]

```


## Usage

### As a cron job

```cron
* * * * * /usr/bin/gh_taskw
```
