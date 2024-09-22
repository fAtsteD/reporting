import pytest
from sqlalchemy.orm import Session

import app
from models.kind import Kind
from tests.conftest import ReportingConfigFixture


def test_add_kind(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
    database_session: Session,
) -> None:
    reporting_config()
    kind_raw = {
        "alias": "legal-witch",
        "name": "Principal Group Associate",
    }
    output_expected = "Kinds:\n"
    output_expected += f"{kind_raw['alias']} - {kind_raw['name']}\n"

    app.main(["--kind", kind_raw["alias"], kind_raw["name"]])
    output = capsys.readouterr()

    assert output.out == (output_expected)
    saved_kind = database_session.query(Kind).first()
    assert saved_kind is not None
    assert saved_kind.alias == kind_raw["alias"]
    assert saved_kind.name == kind_raw["name"]


def test_show_kinds(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
    database_session: Session,
) -> None:
    reporting_config()
    kinds = [
        Kind(alias="expert-gerbil", name="Lead Program Manager"),
        Kind(alias="smoggy-overcoat", name="Investor Functionality Director"),
        Kind(alias="testy-perennial", name="Future Communications Director"),
    ]
    output_expected = "Kinds:\n"
    for kind in kinds:
        database_session.add(kind)
        output_expected += f"{kind}\n"
    database_session.commit()

    app.main(["--show-kinds"])
    output = capsys.readouterr()

    assert output.out == (output_expected)


def test_show_kinds_empty(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    output_expected = "Kinds:\n"

    app.main(["--show-kinds"])
    output = capsys.readouterr()

    assert output.out == (output_expected)


def test_update_kind(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
    database_session: Session,
) -> None:
    reporting_config()
    kind_raw = {
        "alias": "linear-lilac",
        "name": "Dynamic Program Specialist",
    }
    kind_exist = Kind(alias=kind_raw["alias"], name="Chief Tactics Producer")
    database_session.add(kind_exist)
    database_session.commit()
    output_expected = "Kinds:\n"
    output_expected += f"{kind_raw['alias']} - {kind_raw['name']}\n"

    app.main(["--kind", kind_raw["alias"], kind_raw["name"]])
    output = capsys.readouterr()

    assert output.out == (output_expected)
    saved_kind = database_session.query(Kind).first()
    assert saved_kind is not None
    assert saved_kind.alias == kind_raw["alias"]
    assert saved_kind.name == kind_raw["name"]
