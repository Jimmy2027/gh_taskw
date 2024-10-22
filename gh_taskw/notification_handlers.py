from typing import Callable

from gh_taskw.notification import GhNotification, Reason
from gh_taskw.notifier import NotifierNotification


def handle_ci_notification(gh_notification: GhNotification) -> NotifierNotification:
    return NotifierNotification(
        title=f"GitHub {gh_notification.reason.value}",
        body=gh_notification.subject.title,
        urgency="normal",
    )


NOTIFICATION_REASON_TO_HANDLER: dict[Reason, Callable] = {
    Reason.CI_ACTIVITY: handle_ci_notification
}
