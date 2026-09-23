import pytest
from pydantic import ValidationError

from reporting.config import validation_message
from reporting.config.models import RootConfig


def test_lists_every_problem_on_its_own_line() -> None:
    error = _validation_error({"app": {"minute-round-to": "abc", "work-day-hours": "abc"}})

    assert len(validation_message.describe(error).splitlines()) == 2


def test_prefixes_a_problem_with_the_setting_it_is_about() -> None:
    error = _validation_error({"app": {"minute-round-to": "abc"}})

    assert validation_message.describe(error).startswith("app.minute-round-to: ")


def _validation_error(data: dict) -> ValidationError:
    with pytest.raises(ValidationError) as error:
        RootConfig.model_validate(data)

    return error.value
