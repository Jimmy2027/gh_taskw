import json
import os
import subprocess
from enum import StrEnum
from typing import Callable, List, Optional

from loguru import logger
from pydantic import BaseModel

from gh_taskw.notification import GhNotification, Type
from gh_taskw.handlers.notifier import NotifierNotification


def run_command(
    command: list[str],
    check=False,
    env: Optional[dict] = None,
    shell=False,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
) -> subprocess.CompletedProcess:
    try:
        cwd = os.getcwd()
        logger.debug(f'Running command: "{" ".join(command)}" in cwd: {cwd}')
        result = subprocess.run(
            command,
            stdout=stdout,
            stderr=stderr,
            text=True,
            check=check,
            env=env,
        )
        logger.debug(f"Command completed with return code: {result.returncode}")
        logger.trace(f"Command stdout: {result.stdout}")
        logger.trace(f"Command stderr: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Command '{' '.join(command)}' failed with error: {str(e)} in cwd: {cwd}"
        )
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise e


class ReviewState(StrEnum):
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    COMMENTED = "COMMENTED"
    PENDING = "PENDING"
    DISMISSED = "DISMISSED"


class Author(BaseModel):
    login: str


class Commit(BaseModel):
    oid: str


class Review(BaseModel):
    id: str
    author: Author
    authorAssociation: str
    body: Optional[str]
    submittedAt: str
    includesCreatedEdit: bool
    reactionGroups: List[str]
    state: ReviewState
    commit: Commit


class PRState(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


class PullRequestStatus(BaseModel):
    body: str
    closed: bool
    comments: List[dict]
    reviews: List[Review]
    state: PRState


def get_pr_status(pr_url: str, repo_name: str) -> PullRequestStatus:
    result = run_command(
        [
            "gh",
            "pr",
            "view",
            pr_url,
            "--json",
            "body,closed,comments,state,reviews",
            "--repo",
            repo_name,
        ],
    )
    return PullRequestStatus(**json.loads(result.stdout))


def handle_ci_notification(gh_notification: GhNotification) -> NotifierNotification:
    return NotifierNotification(
        title=f"{gh_notification.reason.value}",
        body=gh_notification.subject.title,
        urgency="normal",
    )


def handle_pr_notification(gh_notification: GhNotification) -> NotifierNotification:
    pr_status = get_pr_status(gh_notification.subject.url.__str__(), gh_notification.repository.full_name)

    return NotifierNotification(
        title=f"{gh_notification.reason.value}",
        body=f"{gh_notification.reason}: {gh_notification.subject.title}\n{gh_notification.subject.url}",
        urgency="normal",
    )

def handle_issue_notification(gh_notification: GhNotification) -> NotifierNotification:
    return NotifierNotification(
        title=f"{gh_notification.reason.value}",
        body=f"{gh_notification.reason}: {gh_notification.subject.title}\n{gh_notification.subject.url}",
        urgency="normal",
    )


NOTIFICATION_TYPE_TO_HANDLER: dict[Type, Callable] = {
    Type.CHECK_SUITE: handle_ci_notification,
    Type.PULL_REQUEST: handle_pr_notification,
    Type.ISSUE: handle_issue_notification,
}
