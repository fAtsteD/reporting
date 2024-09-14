import json
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config_app import config_main
from config_app.class_config import Config
from models.base import Base


class ReportingConfigFixture(Protocol):
    def __call__(self, config: dict = {}) -> None: ...


@pytest.fixture(scope="session")
def database_path() -> str:
    return ":memory:"


@pytest.fixture(scope="session")
def database_session(database_path: str) -> Generator[Session]:
    engine = create_engine("sqlite:///" + database_path, echo=False, future=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    Config.sqlite_session = session
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="session")
def reporting_base_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("reporting")
    Config.program_dir = str(dir.absolute())
    return dir


@pytest.fixture
def reporting_config(
    database_path: str,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    reporting_base_dir: Path,
) -> ReportingConfigFixture:
    config_path = reporting_base_dir / "config.json"
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
    monkeypatch.setattr(config_main, "_sqlalchemy_init", lambda: None)

    def config_save(config: dict = {}) -> None:
        config_union = dict(config_default, **config)
        with config_path.open("w", encoding="utf-8") as config_file:
            json.dump(config_union, config_file)

    return config_save
