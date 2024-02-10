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

    def process_gh_notification(self, reason, subject, repository, url):
        """
        Processes a GitHub notification, adding a task and a tasknote to Taskwarrior.
        """
        task_id = self.add_task(reason, subject, repository)
        self.add_tasknote(subject, reason, task_id, url)

    def add_task(self, reason, subject, repository):
        """
        Adds a task to Taskwarrior and returns the task ID.
        """
        cmd = f'task add "{reason}: {subject}"  proj:{repository} +github +{reason}'
        task_add_return = run_command(cmd.split(" "))
        task_id = int(task_add_return.split(" ")[2].strip().strip("."))
        return task_id

    def add_tasknote(self, subject, reason, task_id, url):
        """
        Adds a tasknote to a Taskwarrior task.
        """
        cmd = f"tasknote {task_id} --create_only"
        tasknote_creation_return = run_command(cmd.split(" "))
        tasknote_path = [e for e in tasknote_creation_return.split("\n") if ".md" in e][
            0
        ]

        metadata = [url, f"title: {subject}", f"type: {reason}"]
        with open(tasknote_path, "a") as textfile:
            textfile.write("\n".join(metadata))