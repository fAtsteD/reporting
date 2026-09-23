import datetime

import pytest


@pytest.fixture
def today() -> datetime.date:
    return datetime.datetime.now(datetime.UTC).date()
