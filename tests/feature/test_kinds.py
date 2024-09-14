import pytest
from sqlalchemy.orm import Session

from app import main
from models.kind import Kind
from tests.conftest import ReportingConfigFixture


def test_show_kinds_empty(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    output_expected = "Kinds:\n"

    main(["--show-kinds"])
    output = capsys.readouterr()

    assert output.out == (output_expected + "\n")


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

    main(["--show-kinds"])
    output = capsys.readouterr()

    assert output.out == (output_expected + "\n")
