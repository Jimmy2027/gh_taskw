#!/usr/bin/env python

"""Tests for `gh_taskw` package."""

from pathlib import Path
import subprocess
from gh_taskw.taskwarrior_handler import TaskwarriorHandler

from gh_taskw import cli
import pandas as pd
import json


def test_taskwarrior_handler():
    tw_handler = TaskwarriorHandler()

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

    assert len(gh_helloworld_tasks)

    # delete all github hello world tasks
    for task in gh_helloworld_tasks:
        subprocess.run(["task", str(task["id"]), "delete"])


if __name__ == "__main__":
    test_taskwarrior_handler()
