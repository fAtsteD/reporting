import dateutil
import pytest

from config_app.class_config import Config
from services.file_parse.file_parse import parse_task
from services.file_parse.task_line import TaskLine

testdata_parse_file = [
    (
        "",
        TaskLine(
            kind=Config.default_kind,
            project=Config.default_project,
        ),
    ),
    (
        "09 00",
        TaskLine(
            kind=Config.default_kind,
            project=Config.default_project,
            time_begin=dateutil.parser.parse("09:00"),
        ),
    ),
    (
        "09 10 - Harum beatae\\-molestiae.",
        TaskLine(
            kind=Config.default_kind,
            project=Config.default_project,
            summary="Harum beatae-molestiae.",
            time_begin=dateutil.parser.parse("09:10"),
        ),
    ),
    (
        "09 10 - inventore \\- modi quia",
        TaskLine(
            kind=Config.default_kind,
            project=Config.default_project,
            summary="inventore - modi quia",
            time_begin=dateutil.parser.parse("09:10"),
        ),
    ),
    (
        "10 30 - Non hic repellendus facere architecto reprehenderit aut dolore est quaerat.",
        TaskLine(
            kind=Config.default_kind,
            project=Config.default_project,
            summary="Non hic repellendus facere architecto reprehenderit aut dolore est quaerat.",
            time_begin=dateutil.parser.parse("10:30"),
        ),
    ),
    (
        "11 45 - Incidunt non omnis ut porro ut nostrum. - eum",
        TaskLine(
            kind="eum",
            project=Config.default_project,
            summary="Incidunt non omnis ut porro ut nostrum.",
            time_begin=dateutil.parser.parse("11:45"),
        ),
    ),
    (
        "12 00 - debitis autem ipsa - quasi - Dynamic Response Associate",
        TaskLine(
            kind="quasi",
            project="Dynamic Response Associate",
            summary="debitis autem ipsa",
            time_begin=dateutil.parser.parse("12:00"),
        ),
    ),
]


def expected_id(expected_task_line: TaskLine):
    return str(expected_task_line)


@pytest.mark.parametrize("line, expected", testdata_parse_file, ids=expected_id)
def test_parse_line_exceptions(line: str, expected: TaskLine) -> None:
    task_line = parse_task(line)
    assert task_line == expected
