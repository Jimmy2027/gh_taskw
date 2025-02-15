"""Console script for gh_taskw."""

import sys
from pathlib import Path

import click

from gh_taskw.notification import GhNotification
from gh_taskw.taskwarrior_handler import TaskwarriorHandler
from gh_taskw.utils import (
    get_notifications,
    mark_notification_as_read,
)


def process_row(row, tw_handler: TaskwarriorHandler):
    # mark the notification as read first to make sure a task is not added twice if the script fails
    if "test" not in row and False:
        mark_notification_as_read(row["id"], env_vars=tw_handler.env)
    tw_handler.process_gh_notification(GhNotification(**row.to_dict()))


@click.command()
def main(args=None):
    """Console script for gh_taskw."""
    taskwarrior_handler = TaskwarriorHandler.from_config(
        Path("~/.config/gh_taskw.toml").expanduser()
    )

    log_fn = (
        taskwarrior_handler.logdir / "gh_notifications.json"
        if taskwarrior_handler.logdir
        else None
    )
    df = get_notifications(log_fn=log_fn, env=taskwarrior_handler.env)
    df = df.head(10)
    if not df.empty:
        df.apply(lambda x: process_row(x, taskwarrior_handler), axis=1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
