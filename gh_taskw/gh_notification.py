from dataclasses import dataclass
from loguru import logger


def format_url(url):
    """
    Formats a GitHub api URL to a normal url.
    """
    if url:
        url = (
            url.replace("api.", "").replace("/repos/", "/").replace("/pulls/", "/pull/")
        )
    return url


def get_url(notification_dict):
    if (
        "subject" in notification_dict
        and isinstance(notification_dict["subject"], dict)
        and "url" in notification_dict["subject"]
        and notification_dict["subject"]["url"]
    ):
        return format_url(notification_dict["subject"]["url"])
    elif "url" in notification_dict:
        return format_url(notification_dict["url"])
    else:
        return ""


def get_subject(notification_dict):
    if "subject" in notification_dict and isinstance(
        notification_dict["subject"], dict
    ):
        return notification_dict["subject"].get("title", "")
    else:
        return notification_dict["subject"]


def get_repository(notification_dict):
    if "repository" in notification_dict and isinstance(
        notification_dict["repository"], dict
    ):
        return notification_dict["repository"].get("name", "")
    else:
        return ""


def get_owner(notification_dict):
    try:
        return notification_dict["repository"]["owner"]["login"]
    except:
        return ""


@dataclass
class GhNotification:
    """Base class for GitHub notification."""

    reason: str
    subject: str
    repository: str
    url: str
    owner: str
    id: int

    @classmethod
    def from_notification_dict(cls, notification_dict: dict):
        logger.debug(f"Creating GhNotification from {notification_dict}")
        url = get_url(notification_dict)
        return cls(
            reason=notification_dict["reason"],
            subject=get_subject(notification_dict),
            repository=get_repository(notification_dict),
            url=url,
            owner=get_owner(notification_dict),
            id=int(url.split("/")[-1]),
        )
