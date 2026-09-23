import hashlib
import os
import time
from collections.abc import Generator

import pytest

_DEFAULT_FAKER_SEED = 20260820
_FAKER_SEED_VARIABLE = "REPORTING_TEST_FAKER_SEED"

pytest_plugins = [
    "tests.fixtures.reporting_config",
    "tests.fixtures.cli",
    "tests.fixtures.clock",
    "tests.fixtures.database",
    "tests.fixtures.jira",
    "tests.fixtures.portal",
    "tests.fixtures.tracking_file",
]

_session_faker_seed = int(os.environ.get(_FAKER_SEED_VARIABLE) or _DEFAULT_FAKER_SEED)


@pytest.fixture(autouse=True)
def faker_seed(request: pytest.FixtureRequest) -> int:
    digest = hashlib.sha256(f"{_session_faker_seed}:{request.node.nodeid}".encode()).digest()

    return int.from_bytes(digest[:4], "big")


def pytest_report_header() -> str:
    return f"faker seed: {_session_faker_seed} (set {_FAKER_SEED_VARIABLE} to reproduce)"


@pytest.fixture(scope="session", autouse=True)
def test_environment(tmp_path_factory: pytest.TempPathFactory) -> Generator[None]:
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("COLUMNS", "100")
        patch.setenv("NO_COLOR", "1")
        patch.setenv("TERM", "dumb")
        patch.setenv("TZ", "UTC")
        patch.setenv("XDG_CONFIG_HOME", str(tmp_path_factory.mktemp("config")))
        patch.delenv("FORCE_COLOR", raising=False)
        time.tzset()

        yield

    time.tzset()
