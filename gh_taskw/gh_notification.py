from dataclasses import dataclass

from loguru import logger


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
        subject = get_subject(notification_dict)
        repository = get_repository(notification_dict)
        owner = get_owner(notification_dict)

        try:
            id = int(url.split("/")[-1])
        except ValueError:
            logger.error(f"Could not extract ID from URL: {url}")
            id = 0

        return cls(
            reason=notification_dict["reason"],
            subject=subject,
            repository=repository,
            url=url,
            owner=owner,
            id=id,
        )

    def __post_init__(self):
        if self.reason == "ci_activity":
            workflow_name = self.subject.split(" ")[0]
            self.url = f"https://github.com/{self.owner}/{self.repository}/actions/workflows/{workflow_name}.yml"
