#!/usr/bin/env python

"""Tests for `gh_taskw` package."""

from pathlib import Path
import subprocess
import tempfile
from gh_taskw.notification import Notification
from gh_taskw.taskwarrior_handler import TaskwarriorHandler

from gh_taskw import cli
import pandas as pd
import json

gh_taskw_tasknote_config = 'tasknote_config = "{tasknote_config}"'

GH_TASKW_CONFIG = """
# ignore notifications from ci runs for example
ignore_notification_reasons = ["ci_activity"]

high_priority_reasons = ["review_requested"]
add_task_for_reasons = ["review_requested"]

"""

tasknote_config = """
notes_dir = "{notes_dir}"
"""


def prepare_config(tmpdir, with_tasknote: bool):
    config_fn = tmpdir / "gh_taskw.toml"
    tasknote_config_fn = tmpdir / "tasknote.toml"

    gh_taskw_tasknote_config.format(tasknote_config=tasknote_config_fn)

    if with_tasknote:
        gh_taskw_config = (
            GH_TASKW_CONFIG + f'\ntasknote_config = "{tasknote_config_fn}"\n'
        )
    else:
        gh_taskw_config = GH_TASKW_CONFIG

    config_fn.write_text(gh_taskw_config)
    tasknote_config_fn.write_text(tasknote_config.format(notes_dir=tmpdir / "notes"))

    return config_fn


def test_taskwarrior_handler(with_tasknote: bool):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_fn = prepare_config(Path(tmpdir), with_tasknote=with_tasknote)

        tw_handler = TaskwarriorHandler.from_config(config_fn)

        example_notification_fn = (
            Path(__file__).parent / "test_data" / "example_notification.json"
        )
        df = pd.DataFrame(json.loads(example_notification_fn.read_text()))

        df.apply(lambda x: cli.process_row(x, tw_handler=tw_handler), axis=1)

        # get all tasks with github tag
        gh_helloworld_tasks = json.loads(
            subprocess.check_output(
                ["task", "status:pending", "proj:Hello-World", "+github", "export"]
            ).decode("utf-8")
        )

        # check that the task has been created
        assert len(gh_helloworld_tasks)

        if with_tasknote:
            # check that there is at least one tasknote in the notes directory
            assert len(list(Path(tw_handler.tasknote_handler.notes_dir).glob("*.md")))

        # delete all github hello world tasks
        for task in gh_helloworld_tasks:
            subprocess.run(["task", str(task["id"]), "delete"])


def get_log():
    logfn = Path("~/.local/logs/gh_taskw_.json").expanduser()

    with open(logfn, "r") as f:
        log_dict = {k:v for k,v in json.load(f).items() if v}

    # the keys are the dates. Get the last one
    last_log = [d for k in sorted(log_dict.keys()) for d in log_dict[k] if log_dict[k]]
    for log in last_log:
        notification = Notification(**log)
        fsfsag = 0
    df = pd.DataFrame(last_log)
    df["test"] = True

    taskwarrior_handler = TaskwarriorHandler.from_config(
        Path("~/.config/gh_taskw.toml").expanduser()
    )
    df.apply(lambda x: cli.process_row(x, taskwarrior_handler), axis=1)
    taskwarrior_handler.handle_closed_prs()


if __name__ == "__main__":
    get_log()
    # test_taskwarrior_handler(True)
