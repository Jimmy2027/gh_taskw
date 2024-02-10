"""Console script for gh_taskw."""

import os
import sys
import click

from gh_taskw.utils import (
    get_notifications,
    log_errors,
    mark_notification_as_read,
    run_command,
)
from gh_taskw.taskwarrior_handler import TaskwarriorHandler


@log_errors
def process_row(row, tw_handler: TaskwarriorHandler):
    # mark the notification as read first to make sure a task is not added twice if the script fails
    if not 'test' in row:
        mark_notification_as_read(row["id"])
    if row["reason"] != "ci_activity":
        # send a notification to the system
        run_command(
            ["notify-send", "GitHub", f'{row["reason"]}: {row["subject"]["title"]}']
        )

        tw_handler.process_gh_notification(
            reason=row["reason"],
            subject=row["subject"]["title"],
            repository=row["repository"]["name"],
            url=row["subject"]["url"],
        )


@click.command()
def main(args=None):
    """Console script for gh_taskw."""
    os.system("notify-send 'GitHub' 'Fetching notifications...'")
    taskwarrior_handler = TaskwarriorHandler()
    df = get_notifications()
    if not df.empty:
        df.apply(lambda x: process_row(x, taskwarrior_handler), axis=1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
