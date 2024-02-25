from dataclasses import dataclass


def format_url(url):
    """
    Formats a GitHub api URL to a normal url.
    """
    if url:
        url = (
            url.replace("api.", "").replace("/repos/", "/").replace("/pulls/", "/pull/")
        )
    return url


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
        url = format_url(notification_dict["subject"].get("url", ""))
        return cls(
            reason=notification_dict["reason"],
            subject=notification_dict["subject"]["title"],
            repository=notification_dict["repository"]["name"],
            url=url,
            owner=notification_dict["repository"]["owner"]["login"],
            id=int(url.split("/")[-1]),
        )
