from typing import NamedTuple, Protocol

import pytest

from reporting.cli import main


class CliResult(NamedTuple):
    err: str
    exit_code: int
    out: str


class RunCli(Protocol):
    def __call__(self, *cli_args: str) -> CliResult: ...


@pytest.fixture
def run_cli(capsys: pytest.CaptureFixture[str]) -> RunCli:
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
