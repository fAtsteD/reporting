from collections.abc import Callable
from typing import NamedTuple, Protocol

import pytest
from sqlalchemy.orm import Session

from reporting.cli import main


class CliResult(NamedTuple):
    err: str
    exit_code: int
    out: str


class ConfirmationFake:
    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.questions: list[str] = []
        self._answers: list[str] = []
        self._answer_with: Callable[[str], str] | None = None
        monkeypatch.setattr("builtins.input", self._ask)

    def answer(self, *answers: str) -> None:
        self._answers.extend(answers)

    def answer_with(self, answer_with: Callable[[str], str]) -> None:
        self._answer_with = answer_with

    def _ask(self, question: str) -> str:
        self.questions.append(question)

        if self._answer_with is not None:
            return self._answer_with(question)

        return self._answers.pop(0) if self._answers else "n"


class RunCli(Protocol):
    def __call__(self, *cli_args: str) -> CliResult: ...


@pytest.fixture
def confirmation(monkeypatch: pytest.MonkeyPatch) -> ConfirmationFake:
    return ConfirmationFake(monkeypatch)


@pytest.fixture
def run_cli(capsys: pytest.CaptureFixture[str], database_session: Session) -> RunCli:
    def invoke(*cli_args: str) -> CliResult:
        exit_code = 0

        try:
            main.run(list(cli_args))
        except SystemExit as exit_error:
            assert isinstance(exit_error.code, int)
            exit_code = exit_error.code

        captured = capsys.readouterr()

        if exit_code == 0:
            assert captured.err == ""

        return CliResult(err=captured.err, exit_code=exit_code, out=captured.out)

    return invoke
