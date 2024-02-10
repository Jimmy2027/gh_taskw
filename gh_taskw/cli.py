"""Console script for gh_taskw."""

from pathlib import Path
import sys
import click

from gh_taskw.utils import (
    get_notifications,
    log_errors,
    mark_notification_as_read,
)
from gh_taskw.taskwarrior_handler import TaskwarriorHandler


@log_errors
def process_row(row, tw_handler: TaskwarriorHandler):
    # mark the notification as read first to make sure a task is not added twice if the script fails
    if not "test" in row:
        mark_notification_as_read(row["id"])
    tw_handler.process_gh_notification(
        reason=row["reason"],
        subject=row["subject"]["title"],
        repository=row["repository"]["name"],
        url=row["subject"].get("url", ""),
    )


@click.command()
def main(args=None):
    """Console script for gh_taskw."""
    taskwarrior_handler = TaskwarriorHandler.from_config(
        Path("~/.config/gh_taskw.toml").expanduser()
    )
    df = get_notifications()
    if not df.empty:
        df.apply(lambda x: process_row(x, taskwarrior_handler), axis=1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
