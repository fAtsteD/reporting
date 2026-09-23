import re
from collections.abc import Sequence
from io import StringIO

from rich.console import Console, RenderableType

from reporting.cli.views import theme

_BOX_CHARACTERS = "─│╭╮╰╯"
_CONSOLE_WIDTH = 100

_WHITESPACE = re.compile(r"\s+")


def assert_lines(output: str, expected: Sequence[str]) -> None:
    assert [_WHITESPACE.sub(" ", line) for line in lines(output)] == list(expected)


def flat_text(text: str) -> str:
    return _WHITESPACE.sub(" ", " ".join(lines(text)))


def lines(text: str) -> list[str]:
    stripped_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip().strip(_BOX_CHARACTERS).strip()

        if line:
            stripped_lines.append(line)

    return stripped_lines


def render(renderable: RenderableType) -> str:
    output = StringIO()
    console = Console(
        emoji=False,
        file=output,
        highlight=False,
        markup=False,
        no_color=True,
        theme=theme.THEME,
        width=_CONSOLE_WIDTH,
    )
    console.print(renderable)

    return output.getvalue()
