import pytest

from reporting.config import config_file
from reporting.config.exceptions import ConfigError
from tests.fixtures.reporting_config import ReportingConfigFixture


def test_reads_no_data_when_the_file_is_missing() -> None:
    config_file.config_path().unlink(missing_ok=True)

    assert config_file.read_data() == {}


def test_reads_the_settings_from_the_file(reporting_config: ReportingConfigFixture) -> None:
    reporting_config({"jira": {"server": "https://jira.example.com"}})

    assert config_file.read_data()["jira"]["server"] == "https://jira.example.com"


def test_rejects_a_file_that_is_not_a_json_object(reporting_config: ReportingConfigFixture) -> None:
    config_file.config_path().write_text("[1, 2]", encoding="utf-8")

    with pytest.raises(ConfigError, match="has to contain a JSON object"):
        config_file.read_data()


def test_rejects_a_file_that_is_not_json(reporting_config: ReportingConfigFixture) -> None:
    config_file.config_path().write_text("{not json", encoding="utf-8")

    with pytest.raises(ConfigError, match="is not valid JSON"):
        config_file.read_data()


def test_reports_an_invalid_setting_with_its_location(reporting_config: ReportingConfigFixture) -> None:
    config_file.config_path().write_text('{"app": {"minute-round-to": "abc"}}', encoding="utf-8")

    with pytest.raises(ConfigError, match="app.minute-round-to: "):
        config_file.load()


def test_writes_the_settings_back_as_sorted_json(reporting_config: ReportingConfigFixture) -> None:
    root_config = config_file.load()
    root_config.jira.server = "https://jira.example.com"

    config_file.save(root_config)

    assert config_file.read_data()["jira"]["server"] == "https://jira.example.com"
