from enum import StrEnum
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, Field


class Owner(BaseModel):
    name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    login: str
    id: int
    node_id: str
    avatar_url: AnyUrl
    gravatar_id: Optional[str]
    url: AnyUrl
    html_url: AnyUrl
    followers_url: AnyUrl
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: AnyUrl
    organizations_url: AnyUrl
    repos_url: AnyUrl
    events_url: str
    received_events_url: AnyUrl
    type: str
    site_admin: bool
    starred_at: Optional[str] = Field(default=None)


class Permissions(BaseModel):
    admin: Optional[bool] = Field(default=None)
    maintain: Optional[bool] = Field(default=None)
    push: Optional[bool] = Field(default=None)
    triage: Optional[bool] = Field(default=None)
    pull: Optional[bool] = Field(default=None)


class CodeOfConduct(BaseModel):
    key: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    url: Optional[AnyUrl] = Field(default=None)
    body: Optional[str] = Field(default=None)
    html_url: Optional[AnyUrl] = Field(default=None)


class License(BaseModel):
    key: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    spdx_id: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    node_id: Optional[str] = Field(default=None)


class SecurityFeature(BaseModel):
    status: Optional[str] = Field(default=None)


class SecurityAndAnalysis(BaseModel):
    advanced_security: Optional[SecurityFeature] = Field(default=None)
    dependabot_security_updates: Optional[SecurityFeature] = Field(default=None)
    secret_scanning: Optional[SecurityFeature] = Field(default=None)
    secret_scanning_push_protection: Optional[SecurityFeature] = Field(default=None)
    secret_scanning_non_provider_patterns: Optional[SecurityFeature] = Field(
        default=None
    )
    secret_scanning_ai_detection: Optional[SecurityFeature] = Field(default=None)


class Repository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    owner: Owner
    private: bool
    html_url: AnyUrl
    description: Optional[str] = Field(default=None)
    fork: Optional[bool] = Field(default=None)
    url: AnyUrl
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: Optional[AnyUrl] = Field(default=None)
    deployments_url: Optional[AnyUrl] = Field(default=None)
    downloads_url: Optional[AnyUrl] = Field(default=None)
    events_url: Optional[AnyUrl] = Field(default=None)
    forks_url: Optional[AnyUrl] = Field(default=None)
    git_commits_url: Optional[str] = Field(default=None)
    git_refs_url: Optional[str] = Field(default=None)
    git_tags_url: Optional[str] = Field(default=None)
    git_url: Optional[str] = Field(default=None)
    issue_comment_url: Optional[str] = Field(default=None)
    issue_events_url: Optional[str] = Field(default=None)
    issues_url: Optional[str] = Field(default=None)
    keys_url: Optional[str] = Field(default=None)
    labels_url: Optional[str] = Field(default=None)
    languages_url: Optional[AnyUrl] = Field(default=None)
    merges_url: Optional[AnyUrl] = Field(default=None)
    milestones_url: Optional[str] = Field(default=None)
    notifications_url: Optional[str] = Field(default=None)
    pulls_url: Optional[str] = Field(default=None)
    releases_url: Optional[str] = Field(default=None)
    ssh_url: Optional[str] = Field(default=None)
    stargazers_url: Optional[AnyUrl] = Field(default=None)
    statuses_url: Optional[str] = Field(default=None)
    subscribers_url: Optional[AnyUrl] = Field(default=None)
    subscription_url: Optional[AnyUrl] = Field(default=None)
    tags_url: Optional[AnyUrl] = Field(default=None)
    teams_url: Optional[AnyUrl] = Field(default=None)
    trees_url: Optional[str] = Field(default=None)
    clone_url: Optional[str] = Field(default=None)
    mirror_url: Optional[str] = Field(default=None)
    hooks_url: Optional[AnyUrl] = Field(default=None)
    svn_url: Optional[str] = Field(default=None)
    homepage: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)
    forks_count: Optional[int] = Field(default=None)
    stargazers_count: Optional[int] = Field(default=None)
    watchers_count: Optional[int] = Field(default=None)
    size: Optional[int] = Field(default=None)
    default_branch: Optional[str] = Field(default=None)
    open_issues_count: Optional[int] = Field(default=None)
    is_template: Optional[bool] = Field(default=None)
    topics: Optional[List[str]] = Field(default=None)
    has_issues: Optional[bool] = Field(default=None)
    has_projects: Optional[bool] = Field(default=None)
    has_wiki: Optional[bool] = Field(default=None)
    has_pages: Optional[bool] = Field(default=None)
    has_downloads: Optional[bool] = Field(default=None)
    has_discussions: Optional[bool] = Field(default=None)
    archived: Optional[bool] = Field(default=None)
    disabled: Optional[bool] = Field(default=None)
    visibility: Optional[str] = Field(default=None)
    pushed_at: Optional[str] = Field(default=None)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)
    permissions: Optional[Permissions] = Field(default=None)
    role_name: Optional[str] = Field(default=None)
    temp_clone_token: Optional[str] = Field(default=None)
    delete_branch_on_merge: Optional[bool] = Field(default=None)
    subscribers_count: Optional[int] = Field(default=None)
    network_count: Optional[int] = Field(default=None)
    code_of_conduct: Optional[CodeOfConduct] = Field(default=None)
    license: Optional[License] = Field(default=None)
    security_and_analysis: Optional[SecurityAndAnalysis] = Field(default=None)


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
    REPOSITORY_INVITATION = "RepositoryInvitation"


class Subject(BaseModel):
    title: str
    # none for ci for example
    url: AnyUrl | None
    latest_comment_url: AnyUrl | None
    type: Type


class GhNotification(BaseModel):
    id: str
    repository: Repository
    subject: Subject
    reason: Reason
    unread: bool
    updated_at: str
    last_read_at: Optional[str]
    url: str
    subscription_url: str
