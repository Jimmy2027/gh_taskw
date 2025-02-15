import os
import sys
from pathlib import Path
from typing import Optional

import tomllib
from loguru import logger

from gh_taskw.handlers.notifier import Notifier, NotifierNotification
from gh_taskw.handlers.rss_handler import RSSHandler
from gh_taskw.notification import GhNotification, Reason
from gh_taskw.notification_handlers import NOTIFICATION_TYPE_TO_HANDLER


class TaskwarriorHandler:
    """
    Class used to add gh notifications to Taskwarrior.

    ...

    Methods
    -------
    run_command(cmd)
        Executes a command using subprocess and returns the output.
    process_gh_notification(reason, subject, repository, title, url)
        Processes a GitHub notification, adding a task and a tasknote to Taskwarrior.
    add_task(reason, subject, repository)
        Adds a task to Taskwarrior and returns the task ID.
    add_tasknote(subject, reason, task_id, url)
        Adds a tasknote to a Taskwarrior task.
    """

    def __init__(
        self,
        ignore_notification_reasons=None,
        high_priority_reasons=None,
        add_task_for_reasons=None,
        logdir: Optional[Path] = None,
        loglevel: str = "ERROR",
        notifier: Optional[Notifier] = None,
        github_token: Optional[str] = None,
    ):
        self.tasknote_fn = None
        self.gh_token = github_token
        self.ignore_notification_reasons: list[Reason] = (
            ignore_notification_reasons or []
        )
        self.add_task_for_reasons = add_task_for_reasons or []
        self.high_priority_reasons: list[Reason] = high_priority_reasons or []

        self.logdir = logdir

        self.rss_handler = RSSHandler()

        self.notifier: Optional[Notifier] = notifier

        self.env = self._set_env()
        self._setup_logger(loglevel)

    def _setup_logger(self, loglevel: str):
        if self.logdir:
            self.logdir.mkdir(parents=True, exist_ok=True)
            logdir = self.logdir
        else:
            logdir = sys.stderr

        logger.add(
            logdir / "gh_taskw.log",
            rotation="500 MB",
            level=loglevel,
            format="{time} {level} {message}",
        )

    def _set_env(self):
        env = os.environ.copy()
        if self.gh_token is not None:
            env["GH_TOKEN"] = self.gh_token
        return env

    def _send_notification(self, notifier_notification: NotifierNotification):
        if self.notifier:
            self.notifier.notify(notifier_notification)

    @classmethod
    def from_config(cls, config_file: Optional[Path] = None):
        if config_file is None:
            config_file = Path("~/.config/gh_taskw.toml").expanduser()

        toml_config = config_file.read_text()

        toml_dict = tomllib.loads(toml_config)

        # check if logfile is set
        toml_dict["logdir"] = (
            Path(toml_dict["logdir"]).expanduser() if "logdir" in toml_dict else None
        )

        # check if gh token is set
        notification_config = toml_dict.pop("notifications", None)

        return cls(
            notifier=(
                Notifier.from_config(notification_config)
                if notification_config
                else None
            ),
            **toml_dict,
        )

    def process_gh_notification(self, gh_notification: GhNotification):
        """
        Processes a GitHub notification, adding a task and a tasknote to Taskwarrior.
        """
        logger.debug(f"Processing notification: {gh_notification}")
        if gh_notification.reason in self.ignore_notification_reasons:
            return

        # send a notification to the system
        self._send_notification(
            NOTIFICATION_TYPE_TO_HANDLER[gh_notification.subject.type](gh_notification)
        )
        self.rss_handler.handle_notification(gh_notification)
