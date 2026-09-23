import json

from reporting.config import config_file
from tests.assertions import cli_output
from tests.fixtures.cli import RunCli
from tests.fixtures.reporting_config import ReportingConfigFixture


def test_config_list_marks_a_missing_config_file(
    run_cli: RunCli,
) -> None:
    config_file.config_path().unlink(missing_ok=True)

    rendered = cli_output.flat_text(run_cli("config", "list").out)

    assert "(does not exist, every value is a default)" in rendered


def test_config_list_shows_the_config_file_path(
    run_cli: RunCli,
) -> None:
    rendered = cli_output.flat_text(run_cli("config", "list").out)

    assert str(config_file.config_path()) in rendered
    assert "does not exist" not in rendered


def test_config_reports_an_invalid_config_file_as_one_error_line(
    run_cli: RunCli,
) -> None:
    config_file.config_path().write_text('{"app": {"minute-round-to": "abc"}}', encoding="utf-8")

    failure = run_cli("config", "list")

    assert failure.exit_code == 1
    assert failure.out == ""
    rendered = cli_output.flat_text(failure.err)
    assert rendered.startswith("Error Config file ")
    assert "app.minute-round-to: " in rendered
    assert len(cli_output.lines(failure.err)) == 3


def test_config_set_prints_the_error_and_exits_with_one(
    run_cli: RunCli,
) -> None:
    failure = run_cli("config", "set", "app.minute-round-to", "abc")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert "app.minute-round-to" in cli_output.flat_text(failure.err)


def test_config_set_rewrites_the_file_without_unknown_sections(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"legacy-section": {"legacy-setting": "value"}})

    run_cli("config", "set", "jira.server", "https://jira.example.com")

    saved = json.loads(config_file.config_path().read_text(encoding="utf-8"))
    assert "legacy-section" not in saved
    assert saved["jira"]["server"] == "https://jira.example.com"


def test_config_set_then_get_shows_the_new_value(
    run_cli: RunCli,
) -> None:
    saved = cli_output.flat_text(run_cli("config", "set", "app.minute-round-to", "25").out)

    assert "app.minute-round-to 25" in saved
    assert "saved" in saved
    assert "app.minute-round-to 25" in cli_output.flat_text(run_cli("config", "get", "app.minute-round-to").out)


def test_config_set_writes_the_value_to_the_config_file(
    run_cli: RunCli,
) -> None:
    run_cli("config", "set", "app.minute-round-to", "25")

    assert json.loads(config_file.config_path().read_text(encoding="utf-8"))["app"]["minute-round-to"] == 25


def test_config_unset_removes_one_item_from_a_list_setting(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"omit-task": ["lunch", "break"]}})

    result = run_cli("config", "unset", "app.omit-task", "lunch")

    assert "app.omit-task break" in cli_output.flat_text(result.out)


def test_config_unset_removes_the_value_from_the_config_file(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"jira": {"login": "someone", "password": "secret"}})

    result = run_cli("config", "unset", "jira.password")

    assert "jira.password (empty)" in cli_output.flat_text(result.out)
    saved = json.loads(config_file.config_path().read_text(encoding="utf-8"))
    assert saved["jira"] == {"issue-key-base": [], "login": "someone", "password": "", "server": ""}
