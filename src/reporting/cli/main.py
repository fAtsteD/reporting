import sys

import typer
from typer import rich_utils
from typer._click import ClickException

from reporting import config
from reporting.cli import views
from reporting.cli.app import app
from reporting.exceptions import ReportingError

ERROR_EXIT_CODE = 1
INTERRUPT_EXIT_CODE = 130


def run(cli_args: list[str] | None = None) -> None:
    try:
        config.reload()
        exit_code: int | None = app(args=cli_args, standalone_mode=False)
    except ClickException as error:
        rich_utils.rich_format_error(error)
        raise SystemExit(error.exit_code) from error
    except typer.Abort as error:
        rich_utils.rich_abort_error()
        raise SystemExit(ERROR_EXIT_CODE) from error
    except KeyboardInterrupt as error:
        raise SystemExit(INTERRUPT_EXIT_CODE) from error
    except ReportingError as error:
        print(views.render_error(error), file=sys.stderr)
        raise SystemExit(ERROR_EXIT_CODE) from error

    if exit_code:
        raise SystemExit(exit_code)
