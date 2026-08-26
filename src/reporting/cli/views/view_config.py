from collections.abc import Sequence
from pathlib import Path
from typing import Any

from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from reporting.cli.views import layout, theme
from reporting.config import config_access

EMPTY_NOTE = "(empty)"
LOCATION_LABEL = "Config file: "
MISSING_FILE_NOTE = "(does not exist, every value is a default)"
SECTION_INDENT = (0, 0, 0, 2)
SECTION_KEY_HINT = "  {section}.*"
SECTION_SEPARATOR = "."
SECTION_TITLES = {
    "app": "App",
    "dictionary": "Dictionary",
    "jira": "Jira",
    "qatestlab-portal": "QATestLab Portal",
}
TITLE = "Configuration"


def render(config_file_path: Path, is_existing: bool, values: Sequence[tuple[str, Any, str]]) -> Panel:
    location = f"{LOCATION_LABEL}{config_file_path}"

    if not is_existing:
        location = f"{location} {MISSING_FILE_NOTE}"

    renderables: list[RenderableType] = [Text(location, style=theme.STYLE_HINT)]
    sections = _group_by_section(values)
    key_width = max((len(key) for rows in sections.values() for key, _ in rows), default=0)

    for section, rows in sections.items():
        renderables.append(Text(""))
        renderables.append(_render_heading(section))
        renderables.append(Padding(layout.definition_table(rows, key_width), SECTION_INDENT))

    return layout.panel(Group(*renderables), TITLE)


def _group_by_section(values: Sequence[tuple[str, Any, str]]) -> dict[str, list[tuple[str, RenderableType]]]:
    sections: dict[str, list[tuple[str, RenderableType]]] = {}

    for key, value, description in values:
        section, _, name = key.partition(SECTION_SEPARATOR)
        sections.setdefault(section, []).append((name, _render_value(value, description)))

    return sections


def _render_data(value: Any) -> RenderableType:
    if isinstance(value, dict):
        if not value:
            return Text(EMPTY_NOTE, style=theme.STYLE_HINT)

        return layout.entry_table(
            [(entry_key, config_access.format_value(entry)) for entry_key, entry in value.items()]
        )

    if isinstance(value, list):
        if not value:
            return Text(EMPTY_NOTE, style=theme.STYLE_HINT)

        return _render_list(value)

    if value is None or (isinstance(value, str) and not value):
        return Text(EMPTY_NOTE, style=theme.STYLE_HINT)

    return Text(config_access.format_value(value))


def _render_heading(section: str) -> Text:
    heading = Text(SECTION_TITLES.get(section, section), style=theme.STYLE_TITLE)
    heading.append(SECTION_KEY_HINT.format(section=section), style=theme.STYLE_HINT)

    return heading


def _render_list(items: Sequence[Any]) -> Text:
    return Text("\n".join(config_access.format_value(item) for item in items))


def _render_value(value: Any, description: str) -> RenderableType:
    renderables: list[RenderableType] = [_render_data(value)]

    if description:
        renderables.append(Text(description, style=theme.STYLE_HINT))

    return Group(*renderables)
