from dataclasses import dataclass
from enum import StrEnum

from loguru import logger
from pydantic import AnyUrl, BaseModel, ConfigDict, Field, field_validator


def get_url(notification_dict):
    url = ""
    if (
        "subject" in notification_dict
        and isinstance(notification_dict["subject"], dict)
        and "url" in notification_dict["subject"]
    ):
        url = notification_dict["subject"]["url"]
    elif "url" in notification_dict:
        url = notification_dict["url"]

    if url:
        url = (
            url.replace("api.", "").replace("/repos/", "/").replace("/pulls/", "/pull/")
        )
    return url


def get_reason(notification_dict):
    return notification_dict["reason"]


def get_subject(notification_dict):
    return notification_dict["subject"]["title"]


def get_repository(notification_dict):
    return notification_dict["repository"]["name"]


def get_owner(notification_dict):
    return notification_dict["repository"]["owner"]["login"]


class Reason(StrEnum):
    ASSIGN = "assign"
    AUTHOR = "author"
    COMMENT = "comment"
    INVITATION = "invitation"
    MANUAL = "manual"
    MENTION = "mention"
    REVIEW_REQUESTED = "review_requested"
    SECURITY_ALERT = "security_alert"
    STATE_CHANGE = "state_change"
    SUBSCRIBED = "subscribed"
    TEAM_MENTION = "team_mention"
    CI_ACTIVITY = "ci_activity"


class Type(StrEnum):
    ISSUE = "Issue"
    PULL_REQUEST = "PullRequest"
    CHECK_SUITE = "CheckSuite"
    SECURITY_ADVISORY = "SecurityAdvisory"
    PULL_REQUEST_REVIEW = "PullRequestReview"
    PULL_REQUEST_REVIEW_COMMENT = "PullRequestReviewComment"
    COMMIT_COMMENT = "CommitComment"
    ISSUE_COMMENT = "IssueComment"
    RELEASE = "Release"
    REPOSITORY_VULNERABILITY_ALERT = "RepositoryVulnerabilityAlert"


class Subject(BaseModel):
    title: str
    url: AnyUrl
    latest_comment_url: AnyUrl
    type: Type


class Repository(BaseModel):
    id: str
    name: str
    full_name: str
    html_url: AnyUrl
    description: str
    url: AnyUrl
    owner: dict
