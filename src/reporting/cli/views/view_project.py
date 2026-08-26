from collections.abc import Sequence

from rich.panel import Panel
from rich.text import Text

from reporting.cli.views import layout, theme
from reporting.database.models import Project

EMPTY_MESSAGE = "No projects yet"
TITLE = "Projects"


def render(projects: Sequence[Project]) -> Panel:
    if not projects:
        return layout.panel(Text(EMPTY_MESSAGE, style=theme.STYLE_HINT), TITLE)

    return layout.panel(layout.definition_table([(project.alias, project.name) for project in projects]), TITLE)
