import json
from collections.abc import Generator
from typing import Protocol

import pytest

from reporting import config
from reporting.config import config_file

_CONFIG_BASELINE: dict = {
    "app": {
        "minute-round-to": 0,
        "sqlite-database-path": ":memory:",
    },
}


class ReportingConfigFixture(Protocol):
    def __call__(self, config_data: dict | None = None) -> None: ...


@pytest.fixture
def reporting_config() -> Generator[ReportingConfigFixture]:
    config_path = config_file.config_path()

    def config_save(config_data: dict | None = None) -> None:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(_merge_sections(_CONFIG_BASELINE, config_data or {})), encoding="utf-8")
        config.reload()

    config_save()

    yield config_save

    config_path.unlink(missing_ok=True)
    config.reload()


def _merge_sections(baseline: dict, overrides: dict) -> dict:
    merged: dict = {}

    for section_name in sorted(set(baseline) | set(overrides)):
        baseline_section = baseline.get(section_name, {})
        override_section = overrides.get(section_name, {})

        if isinstance(baseline_section, dict) and isinstance(override_section, dict):
            merged[section_name] = dict(baseline_section, **override_section)
        else:
            merged[section_name] = override_section

    return merged
