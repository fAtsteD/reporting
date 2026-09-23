import pytest

from reporting.cli import output


@pytest.mark.parametrize(
    "answer, is_confirmed",
    [
        pytest.param("y", True, id="the confirm answer"),
        pytest.param("n", False, id="another letter"),
        pytest.param("Y", False, id="the confirm answer in upper case"),
        pytest.param("", False, id="no answer"),
    ],
)
def test_confirms_only_the_exact_answer(
    answer: str,
    is_confirmed: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda question: answer)

    assert output.confirm("Send?") is is_confirmed
