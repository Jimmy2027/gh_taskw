from dataclasses import dataclass
from gotify import Gotify
import subprocess
from typing import Optional


URGENCY_LEVELS = {"low": 0, "normal": 1, "critical": 2}


@dataclass
class NotifierNotification:
    title: str
    body: str
    urgency: str = "low"
    timeout: str = "5000"
    icon: Optional[str] = None

    @property
    def urgency_level(self) -> int:
        return URGENCY_LEVELS[self.urgency]


@dataclass
class Notifier:
    """
    Send a notification to the configured notification service.
    """

    notification_system: str
    gotify: Optional[Gotify] = None

    @classmethod
    def from_config(cls, config: dict):
        if config["system"] == "gotify":
            gotify = Gotify(
                base_url=config["base_url"],
                app_token=config["app_token"],
            )
        else:
            gotify = None

        return cls(config["system"], gotify=gotify)

    def _send_notify_send(
        self,
        notification: NotifierNotification,
    ) -> None:
        """Send a notification using notify-send."""
        command = [
            "notify-send",
            notification.title,
            notification.body,
            "-u",
            notification.urgency,
            "-t",
            notification.timeout,
        ]
        if notification.icon:
            command.extend(["-i", notification.icon])
        subprocess.run(command, check=True)

    def _send_gotify(self, notification: NotifierNotification):
        self.gotify.create_message(
            title=notification.title,
            message=notification.body,
            priority=notification.urgency_level,
        )

    def notify(self, notification: NotifierNotification) -> None:
        """Send a notification to the configured notification service."""
        send_methods = {
            "notify_send": self._send_notify_send,
            "gotify": self._send_gotify,
        }
        send_method = send_methods.get(self.notification_system)
        if send_method:
            send_method(notification)
