from rich.console import Console, RenderableType
from rich.text import Text

from reporting.cli.views import theme

CONFIRM_ANSWER = "y"


def _create_console(is_stderr: bool) -> Console:
    return Console(emoji=False, highlight=False, markup=False, stderr=is_stderr, theme=theme.THEME)


_diagnostic_console = _create_console(True)
_result_console = _create_console(False)


def confirm(question: str) -> bool:
    return input(question) == CONFIRM_ANSWER


def print_diagnostic(renderable: RenderableType) -> None:
    _diagnostic_console.print(renderable)


def print_progress(message: str) -> None:
    if not _result_console.is_terminal:
        return

    _result_console.print(Text(message, style=theme.STYLE_HINT))


def print_result(renderable: RenderableType) -> None:
    _result_console.print(renderable)
