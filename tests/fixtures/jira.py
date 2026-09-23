from dataclasses import dataclass
from typing import Any

import jira.client
import jira.exceptions
import pytest

from tests.fixtures.reporting_config import ReportingConfigFixture

JIRA_LOGIN = "login"
JIRA_PASSWORD = "password"
JIRA_SERVER = "https://jira.example.com"

JIRA_CONFIG: dict = {
    "app": {"timezone": "UTC"},
    "jira": {
        "issue-key-base": ["TEST-"],
        "login": JIRA_LOGIN,
        "password": JIRA_PASSWORD,
        "server": JIRA_SERVER,
    },
}


@dataclass(frozen=True)
class Worklog:
    comment: str | None
    key: str
    time_spent: str


class JiraApiFake:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.connections: list[dict] = []
        self.requested_issue_keys: list[str] = []
        self.worklogs: list[Worklog] = []
        self._issues: dict[str, _Issue] = {}
        monkeypatch.setattr(jira.client.JIRA, "__init__", self._connect)
        monkeypatch.setattr(jira.client.JIRA, "issue", self._find_issue)
        monkeypatch.setattr(jira.client.JIRA, "add_worklog", self._add_worklog)

    def add_issue(self, key: str, summary: str = "") -> None:
        self._issues[key] = _Issue(summary=summary)

    def fail_issue(self, key: str, status_code: int = 404, text: str = "") -> None:
        self._issues[key] = _Issue(status_code=status_code, text=text)

    def _add_worklog(self, key: str, time_spent: str, comment: str | None = None) -> bool:
        self.worklogs.append(Worklog(comment=comment, key=key, time_spent=time_spent))

        return True

    def _connect(self, *args: Any, **kwargs: Any) -> None:
        self.connections.append(kwargs)

    def _find_issue(self, key: str) -> "_IssueStub":
        self.requested_issue_keys.append(key)
        issue = self._issues.get(key)

        if issue is None:
            raise jira.exceptions.JIRAError(status_code=404, text=f"Issue does not exist: {key}")

        if issue.status_code:
            raise jira.exceptions.JIRAError(status_code=issue.status_code, text=issue.text)

        return _IssueStub(issue.summary)


@dataclass
class _Issue:
    status_code: int = 0
    summary: str = ""
    text: str = ""


class _IssueFieldsStub:
    def __init__(self, summary: str) -> None:
        self.summary = summary


class _IssueStub:
    def __init__(self, summary: str) -> None:
        self.fields = _IssueFieldsStub(summary)


@pytest.fixture
def jira_api(monkeypatch: pytest.MonkeyPatch) -> JiraApiFake:
    return JiraApiFake(monkeypatch)


@pytest.fixture
def jira_config(reporting_config: ReportingConfigFixture) -> None:
    reporting_config(JIRA_CONFIG)
