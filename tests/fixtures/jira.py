from dataclasses import dataclass, field
from typing import Protocol

import jira.client
import jira.exceptions
import pytest


class IssueFieldsStub:
    def __init__(self, summary: str) -> None:
        self.summary = summary


class IssueStub:
    def __init__(self, summary: str) -> None:
        self.fields = IssueFieldsStub(summary)


@dataclass
class JiraCalls:
    init_arguments: dict = field(default_factory=dict)
    issue_keys: list[str] = field(default_factory=list)
    worklogs: list[tuple[str, str, str | None]] = field(default_factory=list)


class JiraFixture(Protocol):
    def __call__(self, issue_summary: str = "", existing_key_prefix: str = "") -> JiraCalls: ...


@pytest.fixture
def jira_mock(monkeypatch: pytest.MonkeyPatch) -> JiraFixture:

    def monkeypatch_jira_client(issue_summary: str = "", existing_key_prefix: str = "") -> JiraCalls:
        calls = JiraCalls()

        def init_jira(*args, **kwargs) -> None:
            calls.init_arguments.update(kwargs)

        def find_issue(self: jira.client.JIRA, key: str) -> IssueStub:
            calls.issue_keys.append(key)

            if not key.startswith(existing_key_prefix):
                raise jira.exceptions.JIRAError()

            return IssueStub(issue_summary)

        def add_worklog(self: jira.client.JIRA, key: str, time_spent: str, comment: str | None = None) -> bool:
            calls.worklogs.append((key, time_spent, comment))
            return True

        monkeypatch.setattr(jira.client.JIRA, "__init__", init_jira)
        monkeypatch.setattr(jira.client.JIRA, "issue", find_issue)
        monkeypatch.setattr(jira.client.JIRA, "add_worklog", add_worklog)

        return calls

    return monkeypatch_jira_client
