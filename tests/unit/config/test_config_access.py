from typing import Any

import pytest

from reporting.config import config_access
from reporting.config.exceptions import ConfigError
from reporting.config.models import KeyKind, RootConfig


def test_appends_an_item_to_a_list_setting() -> None:
    data: dict = {"app": {"omit-task": ["lunch"]}}

    config_access.set_value(data, "app.omit-task", "break")

    assert data["app"]["omit-task"] == ["lunch", "break"]


def test_creates_the_list_when_the_setting_is_absent() -> None:
    data: dict = {"app": {"omit-task": "not a list"}}

    config_access.set_value(data, "app.omit-task", "lunch")

    assert data["app"]["omit-task"] == ["lunch"]


def test_keeps_a_list_item_that_is_already_there() -> None:
    data: dict = {"app": {"omit-task": ["lunch"]}}

    config_access.set_value(data, "app.omit-task", "lunch")

    assert data["app"]["omit-task"] == ["lunch"]


def test_reads_a_dictionary_entry_from_the_configuration() -> None:
    root = RootConfig.model_validate({"dictionary": {"task": {"l": "lunch"}}})

    assert config_access.get_value(root, "dictionary.task.l") == "lunch"


def test_reads_a_scalar_value_from_the_configuration() -> None:
    root = RootConfig.model_validate({"jira": {"server": "https://jira.example.com"}})

    assert config_access.get_value(root, "jira.server") == "https://jira.example.com"


def test_reads_no_value_for_a_dictionary_entry_that_is_not_set() -> None:
    assert config_access.get_value(RootConfig(), "dictionary.task.l") is None


@pytest.mark.parametrize(
    "key, message",
    [
        pytest.param("", "Configuration key is required", id="an empty key"),
        pytest.param("unknown", 'Unknown configuration key "unknown"', id="an unknown top level key"),
        pytest.param("jira.unknown", 'Unknown configuration key "unknown"', id="an unknown key in a section"),
        pytest.param("jira.server.extra", "is too deep", id="a key below a scalar setting"),
        pytest.param("dictionary.task.l.extra", "is too deep", id="a key below a dictionary entry"),
    ],
)
def test_rejects_a_key_that_does_not_name_a_setting(key: str, message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        config_access.resolve(key)


@pytest.mark.parametrize(
    "data, key, raw_value, message",
    [
        pytest.param({}, "app.minute-round-to", "25", "is not a list", id="a value for a setting that is not a list"),
        pytest.param({}, "app.omit-task", "nope", '"nope" is not in app.omit-task', id="the section is absent"),
        pytest.param(
            {"app": {"omit-task": ["lunch"]}},
            "app.omit-task",
            "nope",
            '"nope" is not in app.omit-task',
            id="the item is not in the list",
        ),
        pytest.param(
            {"app": {"omit-task": "not a list"}},
            "app.omit-task",
            "lunch",
            '"lunch" is not in app.omit-task',
            id="the setting is not a list",
        ),
    ],
)
def test_rejects_removing_a_value_that_cannot_be_removed(
    data: dict,
    key: str,
    message: str,
    raw_value: str,
) -> None:
    with pytest.raises(ConfigError, match=message):
        config_access.unset_value(data, key, raw_value)


@pytest.mark.parametrize(
    "key, message",
    [
        pytest.param("jira", "is a group of settings", id="a whole section"),
        pytest.param("dictionary.task", "is a group of values", id="a whole group of entries"),
    ],
)
def test_rejects_setting_a_group(key: str, message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        config_access.set_value({}, key, "value")


def test_replaces_a_dictionary_entry_that_is_not_a_group() -> None:
    data: dict = {"dictionary": {"task": "not a group"}}

    config_access.set_value(data, "dictionary.task.l", "lunch")

    assert data["dictionary"]["task"] == {"l": "lunch"}


def test_resolves_a_dictionary_entry_to_its_entry_name() -> None:
    assert config_access.resolve("dictionary.task.l").entry_key == "l"


@pytest.mark.parametrize(
    "key, kind",
    [
        pytest.param("jira", KeyKind.SECTION, id="a section"),
        pytest.param("jira.server", KeyKind.SCALAR_FIELD, id="a scalar setting"),
        pytest.param("app.omit-task", KeyKind.LIST_FIELD, id="a list setting"),
        pytest.param("dictionary.task", KeyKind.DICT_FIELD, id="a group of entries"),
        pytest.param("dictionary.task.l", KeyKind.DICT_ENTRY, id="one entry of a group"),
    ],
)
def test_resolves_a_key_to_its_kind(key: str, kind: KeyKind) -> None:
    assert config_access.resolve(key).kind is kind


def test_sets_a_dictionary_entry_under_its_name() -> None:
    data: dict = {}

    config_access.set_value(data, "dictionary.task.l", "lunch")

    assert data["dictionary"]["task"] == {"l": "lunch"}


@pytest.mark.parametrize(
    "key, raw_value, stored",
    [
        pytest.param("jira.server", "https://jira.example.com", "https://jira.example.com", id="text as written"),
        pytest.param("app.minute-round-to", "25", 25, id="a number from its text"),
        pytest.param("app.work-day-hours", "7.5", 7.5, id="a decimal from its text"),
        pytest.param("jira.server", "true", "true", id="a text setting keeps a json word"),
    ],
)
def test_sets_a_scalar_setting(key: str, raw_value: str, stored: Any) -> None:
    data: dict = {}

    config_access.set_value(data, key, raw_value)

    section, _, leaf = key.partition(".")
    assert data[section][leaf] == stored


def test_stores_json_text_in_a_text_list_as_one_literal_item() -> None:
    data: dict = {}

    config_access.set_value(data, "app.omit-task", '["a","b"]')

    assert data["app"]["omit-task"] == ['["a","b"]']


def test_unset_clears_a_list_setting_without_a_value() -> None:
    data: dict = {"app": {"minute-round-to": 25, "omit-task": ["lunch"]}}

    config_access.unset_value(data, "app.omit-task")

    assert data["app"] == {"minute-round-to": 25}


def test_unset_is_silent_when_the_section_is_not_in_the_data() -> None:
    data: dict = {}

    config_access.unset_value(data, "jira.password")

    assert data == {}


def test_unset_removes_a_dictionary_entry() -> None:
    data: dict = {"dictionary": {"task": {"b": "break", "l": "lunch"}}}

    config_access.unset_value(data, "dictionary.task.l")

    assert data["dictionary"]["task"] == {"b": "break"}


def test_unset_removes_a_scalar_setting() -> None:
    data: dict = {"jira": {"login": "someone", "password": "secret"}}

    config_access.unset_value(data, "jira.password")

    assert data["jira"] == {"login": "someone"}


def test_unset_removes_one_item_from_a_list_setting() -> None:
    data: dict = {"app": {"omit-task": ["lunch", "break"]}}

    config_access.unset_value(data, "app.omit-task", "lunch")

    assert data["app"]["omit-task"] == ["break"]


def test_unset_removes_the_section_when_it_becomes_empty() -> None:
    data: dict = {"jira": {"password": "secret"}}

    config_access.unset_value(data, "jira.password")

    assert data == {}
