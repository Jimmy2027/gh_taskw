"""
This script is used to fetch GitHub notifications and process them.

It uses the GitHub CLI to fetch the notifications and convert them into a pandas DataFrame.
Each notification is then processed based on its 'reason' field.
If the 'reason' is not 'ci_activity', a task is added to Taskwarrior with details from the notification.
Regardless of the 'reason', the notification is marked as read using the GitHub CLI.

"""

from pathlib import Path
import subprocess
import json
from typing import Optional
import pandas as pd
from loguru import logger


def run_command(cmd, env_vars: Optional[dict] = None):
    """
    Run a command and return the output as a string.
    """
    result = subprocess.run(cmd, capture_output=True, text=True, env=env_vars)
    if result.returncode != 0:
        raise Exception(
            f"Command failed with error code {result.returncode}\n{result.stderr}"
        )
    return result.stdout


def mylog(issue_dict: dict, logfile: Path = None):
    import json
    from datetime import datetime

    if not issue_dict:
        return

    if not logfile.exists():
        json_dict = {}

    else:
        # Load existing data
        with open(logfile, "r") as textfile:
            json_dict = json.load(textfile)

    # Add new data
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    json_dict[now] = issue_dict

    # Write back to file
    with open(logfile, "w") as textfile:
        json.dump(json_dict, textfile)


def get_notifications(log_fn: Optional[Path] = None, env: Optional[dict] = None):
    """
    Get all unread notifications using the GitHub CLI and return them as a DataFrame.
    """

    # API command to get unread notifications
    notifications_json = run_command(["gh", "api", "notifications"], env_vars=env)

    if log_fn:
        mylog(json.loads(notifications_json), logfile=log_fn)

    # Parse the output into a DataFrame
    notifications_df = pd.DataFrame(json.loads(notifications_json))
    return notifications_df


def log_errors(func):
    """
    Wrapper to log errors and send a notification to the system.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {str(e)}")

    return wrapper


def mark_notification_as_read(notification_id, env_vars: Optional[dict] = None):
    # API command to mark a notification as read
    logger.debug(f"Marking notification {notification_id} as read")
    run_command(
        [
            "gh",
            "api",
            "--silent",
            "--method",
            "PATCH",
            f"notifications/threads/{notification_id}",
        ],
        env_vars=env_vars,
    )
