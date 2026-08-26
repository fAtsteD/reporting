import json

import pytest

from reporting import config
from reporting.config import config_file
from reporting.config.models import RootConfig
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.fixtures.cli import RunCli


def test_list_shows_config_file_path(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    config_path = config_file.config_path()

    missing = run_cli("config", "list")
    assert f"{config_path} (does not exist, every value is a default)" in rendered_output.flat_text(missing.out)

    reporting_config()

    existing = run_cli("config", "list")
    existing_rendered = rendered_output.flat_text(existing.out)
    assert str(config_path) in existing_rendered
    assert "does not exist" not in existing_rendered


def test_list_shows_every_setting_with_description(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("config", "list")

    rendered = rendered_output.flat_text(result.out)

    for section_name, section_info in RootConfig.model_fields.items():
        section = section_info.alias or section_name
        section_config = getattr(config.current, section_name)

        assert f"{section}.*" in rendered

        for field_name, field_info in type(section_config).model_fields.items():
            name = field_info.alias or field_name
            description = field_info.description or ""

            assert name in rendered
            assert description, f"{section}.{name} does not have a description"
            assert description in rendered


@pytest.mark.parametrize(
    "key, value, expected",
    [
        pytest.param("app.timezone", "Europe/Kyiv", "app.timezone Europe/Kyiv", id="text"),
        pytest.param("app.minute-round-to", "25", "app.minute-round-to 25", id="number"),
        pytest.param("dictionary.task.l", "lunch", "dictionary.task.l lunch", id="dictionary entry"),
    ],
)
def test_set_and_get_value(
    expected: str,
    key: str,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    value: str,
) -> None:
    reporting_config()

    saved = rendered_output.flat_text(run_cli("config", "set", key, value).out)
    assert expected in saved
    assert "saved" in saved

    assert expected in rendered_output.flat_text(run_cli("config", "get", key).out)


def test_get_section_prints_every_setting_in_it(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"jira": {"login": "someone", "server": "https://jira.example.com"}})

    rendered = rendered_output.flat_text(run_cli("config", "get", "jira").out)

    assert "jira.login someone" in rendered
    assert "jira.server https://jira.example.com" in rendered
    assert "jira.password (empty)" in rendered


def test_set_saves_value_in_the_config_file(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    run_cli("config", "set", "app.minute-round-to", "25")

    saved = json.loads(config_file.config_path().read_text(encoding="utf-8"))
    assert saved["app"]["minute-round-to"] == 25


def test_set_saves_every_setting_and_drops_unknown_ones(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"legacy-section": {"legacy-setting": "value"}})

    run_cli("config", "set", "jira.server", "https://jira.example.com")

    saved = json.loads(config_file.config_path().read_text(encoding="utf-8"))

    assert "legacy-section" not in saved
    assert saved == config.current.model_dump(by_alias=True)


@pytest.mark.parametrize(
    "key, expected",
    [
        pytest.param("jira.password", "jira.password (empty)", id="text returns to default"),
        pytest.param("dictionary.task.l", "dictionary.task.l (empty)", id="dictionary entry is removed"),
        pytest.param("jira", "jira.login (empty)", id="whole section is reset"),
    ],
)
def test_unset_returns_value_to_default(
    expected: str,
    key: str,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(
        {
            "dictionary": {"task": {"l": "lunch"}},
            "jira": {"login": "someone", "password": "secret"},
        }
    )

    run_cli("config", "unset", key)

    assert expected in rendered_output.flat_text(run_cli("config", "get", key).out)


def test_set_and_unset_list_items(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    added = run_cli("config", "set", "app.omit-task", "lunch")
    assert "app.omit-task lunch" in rendered_output.flat_text(added.out)

    extended = run_cli("config", "set", "app.omit-task", "break")
    assert "app.omit-task lunch break" in rendered_output.flat_text(extended.out)

    repeated = run_cli("config", "set", "app.omit-task", "lunch")
    assert "app.omit-task lunch break" in rendered_output.flat_text(repeated.out)

    removed = run_cli("config", "unset", "app.omit-task", "lunch")
    assert "app.omit-task break" in rendered_output.flat_text(removed.out)

    cleared = run_cli("config", "unset", "app.omit-task")
    assert "app.omit-task (empty)" in rendered_output.flat_text(cleared.out)


def test_set_adds_json_array_as_one_list_item(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("config", "set", "app.omit-task", '["a","b"]')

    assert 'app.omit-task ["a","b"]' in rendered_output.flat_text(result.out)


@pytest.mark.parametrize(
    "arguments, expected_message",
    [
        pytest.param(["config", "get", "unknown.key"], "Unknown configuration key", id="unknown key"),
        pytest.param(["config", "set", "app.minute-round-to", "abc"], "app.minute-round-to", id="wrong type"),
        pytest.param(["config", "set", "dictionary.task", "lunch"], "is a group of values", id="dictionary itself"),
        pytest.param(["config", "unset", "app.minute-round-to", "x"], "is not a list", id="value for not a list"),
        pytest.param(["config", "unset", "app.omit-task", "nope"], '"nope" is not in app.omit-task', id="missing item"),
    ],
)
def test_command_fails_with_message(
    arguments: list[str],
    expected_message: str,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"omit-task": ["lunch"]}})

    failure = run_cli(*arguments)

    assert failure.exit_code == 1
    assert failure.out == ""
    assert expected_message in rendered_output.flat_text(failure.err)


def test_malformed_config_file_fails_with_one_line(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    config_file.config_path().write_text('{"app": {"minute-round-to": "abc"}}', encoding="utf-8")

    failure = run_cli("config", "list")

    assert failure.exit_code == 1
    assert failure.out == ""
    rendered = rendered_output.flat_text(failure.err)
    assert rendered.startswith("Error Config file ")
    assert "app.minute-round-to: " in rendered
    assert len(rendered_output.lines(failure.err)) == 3
