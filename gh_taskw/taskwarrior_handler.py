from pathlib import Path
import tomllib
from typing import Optional
from gh_taskw.utils import run_command


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
    ):
        self.tasknote_handler = tasknote_handler

        self.tasknote_fn = None
        self.ignore_notification_reasons = ignore_notification_reasons

        self.high_priority_reasons = high_priority_reasons or []

    @classmethod
    def from_config(cls, config_file: Optional[Path] = None):
        if config_file is None:
            config_file = Path("~/.config/gh_taskw.toml").expanduser()

        toml_config = config_file.read_text()

        toml_dict = tomllib.loads(toml_config)

        if "tasknote_config" in toml_dict:
            from tasknote.tasknote_handler import TaskNoteHandler

            tasknote_handler = TaskNoteHandler.from_config(
                Path(toml_dict.pop("tasknote_config"))
            )
        else:
            tasknote_handler = None
        return cls(tasknote_handler=tasknote_handler, **toml_dict)

    def process_gh_notification(self, reason, subject, repository, url):
        """
        Processes a GitHub notification, adding a task and a tasknote to Taskwarrior.
        """
        if reason in self.ignore_notification_reasons:
            return

        url = self.format_url(url)

        # send a notification to the system
        cmd = ["dunstify", f"GitHub", f"{reason}: {subject}\n{url}"]

        # critical notifications
        if reason in self.high_priority_reasons:
            cmd.append("-u")
            cmd.append("critical")
        run_command(cmd)

        task_id = self.add_task(reason, subject, repository)

        if self.tasknote_handler:
            self.add_tasknote(subject, reason, task_id, url)

    def add_task(self, reason, subject, repository):
        """
        Adds a task to Taskwarrior and returns the task ID.
        """
        cmd = f'task add "{reason}: {subject}"  proj:{repository} +github +{reason}'
        if reason in self.high_priority_reasons:
            cmd += " priority:H"
        task_add_return = run_command(cmd.split(" "))
        task_id = int(task_add_return.split(" ")[2].strip().strip("."))
        return task_id

    def format_url(self, url):
        """
        Formats a GitHub api URL to a normal url.
        """
        if url:
            url = (
                url.replace("api.", "")
                .replace("/repos/", "/")
                .replace("/pulls/", "/pull/")
            )
        return url

    def add_tasknote(self, subject, reason, task_id, url):
        """
        Adds a tasknote to a Taskwarrior task.
        """
        self.tasknote_fn = self.tasknote_handler.create_note(task_id)

        metadata = [url, f"title: {subject}", f"type: {reason}"]
        with open(self.tasknote_fn, "a") as textfile:
            textfile.write("\n".join(metadata))
