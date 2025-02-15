import json
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from feedgen.feed import FeedGenerator

from gh_taskw.notification import GhNotification, Type


@dataclass
class RSSHandler:
    rss_feed_file: Path = Path("/var/www/localhost/rss/feed.xml")
    github_token: str = ""  # Optional: Use for authenticated API requests

    def __post_init__(self):
        # Initialize Feed Generator
        self.fg = FeedGenerator()
        self.fg.title("GitHub Notifications")
        self.fg.link(href="http://localhost:8080/rss/feed.xml")
        self.fg.description("GitHub Notifications RSS Feed")
        # self.load_existing_feed()

    def load_existing_feed(self):
        """Load existing RSS feed to retain old notifications."""
        if self.rss_feed_file.exists() and self.rss_feed_file.read_text():
            tree = ET.parse(self.rss_feed_file)
            root = tree.getroot()
            for item in root.findall("./channel/item"):
                entry = self.fg.add_entry()
                entry.id(item.find("guid").text)
                entry.title(item.find("title").text)
                entry.link(href=item.find("link").text)
                entry.description(item.find("description").text)
                entry.pubDate(item.find("pubDate").text)

    def format_description(
        self, gh_notification: GhNotification, extra_content=""
    ) -> str:
        """Generate a rich description for the RSS entry, with optional extra content."""
        repo = gh_notification.repository.full_name
        reason = gh_notification.reason.value.replace("_", " ").title()
        subject_type = gh_notification.subject.type.value
        subject_title = gh_notification.subject.title
        updated_at = gh_notification.updated_at
        html_url = gh_notification.subject.url or gh_notification.repository.html_url

        return (
            f"<b>Repository:</b> <a href='{gh_notification.repository.html_url}'>{repo}</a><br>"
            f"<b>Type:</b> {subject_type}<br>"
            f"<b>Title:</b> {subject_title}<br>"
            f"<b>Reason:</b> {reason}<br>"
            f"<b>Updated:</b> {updated_at}<br>"
            f"<a href='{html_url}'>View on GitHub</a><br>"
            f"{extra_content}"
        )

    def fetch_issue_conversation(self, gh_notification: GhNotification) -> str:
        """Fetches all comments for an issue using the GitHub CLI and returns them as formatted HTML."""
        issue_number = gh_notification.subject.url.path.split("/")[-1]

        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "view",
                    issue_number,
                    "--repo",
                    gh_notification.repository.full_name,
                    "--json",
                    "comments",
                    "--jq",
                    ".comments",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            return "<b>Could not fetch issue comments.</b>"

        comments = json.loads(result.stdout)
        formatted_comments = "<b>Issue Comments:</b><br><br>"

        for comment in comments:
            author = comment["author"]["login"]
            body = comment["body"].replace("\n", "<br>")  # Preserve newlines
            formatted_comments += f"<b>{author}:</b> {body}<br><br>"

        return formatted_comments

    def handle_issue_comment(self, gh_notification: GhNotification):
        """Handle notifications for issue comments by fetching the full conversation."""
        conversation_html = self.fetch_issue_conversation(gh_notification)

        self.add_rss_entry(gh_notification, extra_content=conversation_html)

    def handle_pull_request(self, gh_notification: GhNotification):
        """Handle pull request notifications."""
        pr_url = gh_notification.subject.url
        pr_summary = f"<b>Pull Request:</b> <a href='{pr_url}'>View PR</a><br>"
        self.add_rss_entry(gh_notification, extra_content=pr_summary)

    def handle_release(self, gh_notification: GhNotification):
        """Handle release notifications by adding release notes."""
        release_url = gh_notification.subject.url
        release_summary = (
            f"<b>New Release:</b> <a href='{release_url}'>View Release Notes</a><br>"
        )
        self.add_rss_entry(gh_notification, extra_content=release_summary)

    def handle_general(self, gh_notification: GhNotification):
        """Fallback handler for other notification types."""
        self.add_rss_entry(gh_notification)

    def add_rss_entry(self, gh_notification: GhNotification, extra_content=""):
        """Add an entry to the RSS feed."""
        new_entry = self.fg.add_entry()
        new_entry.id(gh_notification.id)
        new_entry.title(
            f"[{gh_notification.repository.name}] {gh_notification.subject.title}"
        )
        new_entry.link(
            href=str(gh_notification.subject.url or gh_notification.repository.html_url)
        )
        new_entry.description(self.format_description(gh_notification, extra_content))
        new_entry.pubDate(gh_notification.updated_at)

        self.save_feed()

    def handle_notification(self, gh_notification: GhNotification):
        """Dispatch notification to the appropriate handler."""
        handlers = {
            Type.ISSUE: self.handle_issue_comment,
            Type.PULL_REQUEST: self.handle_pull_request,
            Type.RELEASE: self.handle_release,
            Type.CHECK_SUITE: None,
        }
        handler = handlers.get(gh_notification.subject.type, self.handle_general)
        if handler:
            handler(gh_notification)

    def save_feed(self):
        """Save the RSS feed to a file"""
        self.fg.rss_file(self.rss_feed_file.as_posix())
