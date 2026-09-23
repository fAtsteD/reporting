import pathlib
from typing import Protocol

import pytest


class TrackingFileFixture(Protocol):
    def __call__(self, lines: list[str] | None = None) -> pathlib.Path: ...


@pytest.fixture
def tracking_file(tmp_path: pathlib.Path) -> TrackingFileFixture:
    file_path = pathlib.Path(tmp_path, "tracking.txt")

    def generate(lines: list[str] | None = None) -> pathlib.Path:
        file_path.write_text("\n".join(lines or []))

        return file_path

    return generate
