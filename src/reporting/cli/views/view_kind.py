from collections.abc import Sequence

from rich.panel import Panel
from rich.text import Text

from reporting.cli.views import layout, theme
from reporting.database.models import Kind

EMPTY_MESSAGE = "No kinds yet"
TITLE = "Kinds"


def render(kinds: Sequence[Kind]) -> Panel:
    if not kinds:
        return layout.panel(Text(EMPTY_MESSAGE, style=theme.STYLE_HINT), TITLE)

    return layout.panel(layout.definition_table([(kind.alias, kind.name) for kind in kinds]), TITLE)
