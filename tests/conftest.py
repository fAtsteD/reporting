import json
import os
import random
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

import pytest
from sqlalchemy.orm import Session

from reporting import database
from reporting.config.app import AppConfig
from reporting.models import Base


class ReportingConfigFixture(Protocol):
    def __call__(self, config: dict = {}) -> None: ...


@pytest.fixture(autouse=True)  # autouse for factory usage in any moment
def database_session(monkeypatch: pytest.MonkeyPatch) -> Generator[Session]:
    database.reconnect(":memory:")

    yield database.session()

    database.session.rollback()
    database.session.remove()
    Base.metadata.drop_all(bind=database.engine)
    database.engine.dispose()


@pytest.fixture(autouse=True)
def faker_seed() -> int:
    return round(random.random() * 1000000)


@pytest.fixture(scope="session")
def reporting_base_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("reporting")
    AppConfig.program_dir = dir.absolute()
    return dir


@pytest.fixture
def reporting_config(
    reporting_base_dir: Path,
) -> Generator[ReportingConfigFixture]:
    config_path = Path(reporting_base_dir, "config.json")
    config_default = {
        "hour-report-path": "",
        "omit-task": [],
        "minute-round-to": 0,
        "dictionary": {
            "task": {},
            "type": {},
            "project": {},
        },
    }

    def config_save(config: dict = {}) -> None:
        config_union = dict(config_default, **config)
        config_path.write_text(json.dumps(config_union), encoding="utf-8")

    yield config_save

    os.remove(config_path)
