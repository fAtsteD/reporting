import json
import os
import random
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from reporting.config_app.class_config import Config
from reporting.models import Base


class ReportingConfigFixture(Protocol):
    def __call__(self, config: dict = {}) -> None: ...


@pytest.fixture(scope="session")
def database_path() -> str:
    return ":memory:"


@pytest.fixture(scope="session")
def database_engine(database_path: str) -> Engine:
    engine = create_engine(
        "sqlite:///" + database_path,
        echo=False,
    )
    return engine


@pytest.fixture(autouse=True)  # autouse for factory usage in any moment
def database_session(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Session]:
    Base.metadata.create_all(bind=database_engine)
    session = Session(bind=database_engine)
    monkeypatch.setattr(Config, "sqlite_session", session)

    yield session

    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=database_engine)


@pytest.fixture(autouse=True)
def faker_seed() -> int:
    return round(random.random() * 1000000)


@pytest.fixture(scope="session")
def reporting_base_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("reporting")
    Config.program_dir = dir.absolute()
    return dir


@pytest.fixture
def reporting_config(
    database_path: str,
    reporting_base_dir: Path,
) -> Generator[ReportingConfigFixture]:
    config_path = Path(reporting_base_dir, "config.json")
    config_default = {
        "hour-report-path": "",
        "sqlite-database-path": database_path,
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
