import datetime

import pytest

from tests.factories.database import ReportFactory
from tests.fixtures.cli import RunCli
from tests.fixtures.jira import JIRA_CONFIG
from tests.fixtures.reporting_config import ReportingConfigFixture


def test_exits_with_the_interrupt_code_when_the_question_is_interrupted(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(JIRA_CONFIG)
    ReportFactory.create(date=datetime.date(2026, 8, 20))

    def interrupt(question: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)

    failure = run_cli("send", "20.08.2026", "--jira")

    assert failure.exit_code == 130
