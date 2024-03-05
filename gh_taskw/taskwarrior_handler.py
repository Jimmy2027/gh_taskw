import json
import os
import subprocess
import sys
import tomllib
from loguru import logger
from pathlib import Path
from typing import Optional

from tasklib import TaskWarrior, Task

from gh_taskw.gh_notification import GhNotification
from gh_taskw.notifier import Notifier, NotifierNotification


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
        tasknote_handler=None,
        ignore_notification_reasons=None,
        high_priority_reasons=None,
        add_task_for_reasons=None,
        logdir: Optional[Path] = None,
        loglevel: str = "ERROR",
        notifier: Optional[Notifier] = None,
        github_token: Optional[str] = None,
    ):
        self.tasknote_handler = tasknote_handler

        self.tasknote_fn = None
        self.gh_token = github_token
        self.ignore_notification_reasons: list[str] = ignore_notification_reasons or []
        self.add_task_for_reasons = add_task_for_reasons or []
        self.high_priority_reasons = high_priority_reasons or []

        self.logdir = logdir

        self.tw = TaskWarrior()

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

        # get tasknote config
        if "tasknote_config" in toml_dict:
            from tasknote.tasknote_handler import TaskNoteHandler

            tasknote_handler = TaskNoteHandler.from_config(
                Path(toml_dict.pop("tasknote_config"))
            )
        else:
            tasknote_handler = None

        # check if logfile is set
        toml_dict["logdir"] = (
            Path(toml_dict["logdir"]).expanduser() if "logdir" in toml_dict else None
        )

        # check if gh token is set
        notification_config = toml_dict.pop("notifications", None)

        return cls(
            tasknote_handler=tasknote_handler,
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

        url = gh_notification.url

        # send a notification to the system
        self._send_notification(
            NotifierNotification(
                title="GitHub",
                body=f"{gh_notification.reason}: {gh_notification.subject}\n{url}",
                urgency=(
                    "critical"
                    if gh_notification.reason in self.high_priority_reasons
                    else "normal"
                ),
            )
        )

        task_id = self.add_task(gh_notification)

        if task_id and self.tasknote_handler:
            self.add_tasknote(gh_notification=gh_notification, task_id=task_id)

    def add_task(self, gh_notification: GhNotification):
        """
        Adds a task to Taskwarrior and returns the task ID.
        """
        logger.info(f"Adding task for GitHub notification: {gh_notification}")

        kwargs = (
            {"priority": "H"}
            if gh_notification.reason in self.high_priority_reasons
            else {}
        )

        if gh_notification.reason in self.add_task_for_reasons:
            tags = [gh_notification.reason, "github"]
            # check if task already exists
            task_exists = len(
                self.tw.tasks.filter(githuburl=gh_notification.url, tags=tags).pending()
            )

            if not task_exists:
                logger.info(
                    f"No existing task found for GitHub notification: {gh_notification}. Creating new task."
                )
                added_task = Task(
                    self.tw,
                    description=f"{gh_notification.reason}: {gh_notification.subject}",
                    project=gh_notification.repository,
                    tags=tags,
                    githuburl=gh_notification.url,
                    **kwargs,
                )
                added_task.save()
                logger.info(f"New task created with ID: {added_task._data['id']}")
            else:
                logger.info(
                    f"Task already exists for GitHub notification: {gh_notification}"
                )

            return added_task._data["id"]
        else:
            logger.info(
                f"GitHub notification reason {gh_notification.reason} not in add_task_for_reasons. Task not added."
            )

    def add_tasknote(self, gh_notification: GhNotification, task_id: int):
        """
        Adds a tasknote to a Taskwarrior task.
        """
        self.tasknote_fn = self.tasknote_handler.create_note(task_id)

        metadata = [
            gh_notification.url,
            f"title: {gh_notification.subject}",
            f"type: {gh_notification.reason}",
        ]
        with open(self.tasknote_fn, "a") as textfile:
            textfile.write("\n".join(metadata))

    def handle_closed_prs(self):
        """
        Close all tasks for closed pr's.
        """
        logger.info("Starting to handle closed PRs")

        pr_tasks = self.tw.tasks.pending().filter(tags=["github", "review_requested"])
        logger.debug(f"Found {len(pr_tasks)} PR tasks")

        for pr_task_obj in pr_tasks._result_cache:
            pr_task_data = pr_task_obj._data
            logger.debug(f"Processing PR task {pr_task_obj}")

            if pr_task_data.get("githuburl"):
                repo = pr_task_data["project"]
                if "pull" in pr_task_data["githuburl"]:
                    owner = pr_task_data["githuburl"].split("/")[3]
                    pr_id = pr_task_data["githuburl"].split("/")[6]
                    gh_api_cmd = [
                        "gh",
                        "api",
                        "-H",
                        "Accept: application/vnd.github+json",
                        f"/repos/{owner}/{repo}/pulls/{pr_id}",
                    ]
                    logger.debug(f"Running command: {' '.join(gh_api_cmd)}")

                    pr_dict = json.loads(
                        subprocess.check_output(gh_api_cmd, env=self.env).decode(
                            "utf-8"
                        )
                    )
                    is_closed = pr_dict["state"] == "closed"
                else:
                    is_closed = True
                    pr_id = pr_task_data["description"].split(":")[-1].strip()
            else:
                is_closed = True
                pr_id = pr_task_data["description"].split(":")[-1].strip()

            if is_closed:
                logger.info(f"PR {pr_id} is closed. Closing task {pr_task_obj}")
                self.notifier.notify(
                    NotifierNotification(
                        title="GitHub",
                        body=f"PR {pr_id} is closed",
                        urgency="normal",
                    )
                )
                # mark task as done
                pr_task_obj.done()
                logger.debug(f"Task {pr_task_obj} marked as done")

        logger.info("Finished handling closed PRs")
