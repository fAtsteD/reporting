from reporting.cli.views import view_kind
from tests.assertions import cli_output
from tests.factories.database import KindFactory


def test_renders_a_note_when_there_are_no_kinds() -> None:
    output = cli_output.render(view_kind.render([]))

    cli_output.assert_lines(output, ["Kinds", "No kinds yet"])


def test_renders_one_row_per_kind() -> None:
    kinds = [KindFactory.build(alias="k1", name="Alpha"), KindFactory.build(alias="k2", name="Beta")]

    output = cli_output.render(view_kind.render(kinds))

    cli_output.assert_lines(output, ["Kinds", "k1 Alpha", "k2 Beta"])
