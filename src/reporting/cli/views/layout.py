from collections.abc import Sequence

from rich.box import ROUNDED
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from reporting.cli.views import theme

ENTRY_PADDING = (0, 2)
ERROR_TITLE = "Error"
FRAME_MARGIN = 2


def definition_table(rows: Sequence[tuple[str, RenderableType]], key_width: int = 0) -> Table:
    table = plain_table()
    table.add_column(min_width=key_width, no_wrap=True, style=theme.STYLE_KEY)
    table.add_column(overflow="fold")

    for key, value in rows:
        table.add_row(key, value)

    return table


def entry_table(rows: Sequence[tuple[str, str]]) -> Table:
    table = Table.grid(padding=ENTRY_PADDING)
    table.add_column(no_wrap=True)
    table.add_column(overflow="fold")

    for entry_key, entry_value in rows:
        table.add_row(entry_key, entry_value)

    return table


def error_panel(body: RenderableType) -> Panel:
    return Panel(
        body,
        border_style=theme.STYLE_ERROR,
        box=ROUNDED,
        title=Text(ERROR_TITLE, style=theme.STYLE_ERROR),
        title_align="left",
    )


def panel(body: RenderableType, title: str, subtitle: str = "") -> Panel:
    return Panel(
        _frame(body, max(len(title), len(subtitle)) + FRAME_MARGIN),
        border_style=theme.STYLE_BORDER,
        box=ROUNDED,
        expand=False,
        subtitle=Text(subtitle, style=theme.STYLE_HINT) if subtitle else None,
        subtitle_align="left",
        title=Text(title, style=theme.STYLE_TITLE),
        title_align="left",
    )


def plain_table() -> Table:
    return Table(box=None, pad_edge=False, padding=(0, 1), show_edge=False, show_header=False)


def _frame(body: RenderableType, min_width: int) -> Table:
    frame = Table(box=None, min_width=min_width, pad_edge=False, padding=0, show_edge=False, show_header=False)
    frame.add_column(overflow="fold")
    frame.add_row(body)

    return frame
