"""``baseconv`` CLI 行为测试（直接调用 main()，配合 capsys）。"""

from __future__ import annotations

import pytest

from base_conversion import __version__
from base_conversion.cli import main


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_positional_conversion(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "255", "10", "16")
    assert code == 0
    assert out.strip() == "FF"


def test_default_bases_are_decimal(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "42")
    assert code == 0
    assert out.strip() == "42"


def test_negative_with_double_dash(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "--", "-123", "10", "2")
    assert code == 0
    assert out.strip() == "-1111011"


def test_negative_with_leading_number_autocorrected(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # 首参数形如 -123：_normalize_argv 自动插入 --
    code, out, _ = _run(capsys, "-123", "10", "2")
    assert code == 0
    assert out.strip() == "-1111011"


def test_option_style(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "-n", "0.1", "-f", "2", "-t", "10")
    assert code == 0
    assert out.strip() == "0.5"


def test_repeating_output(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "1", "3", "10")
    assert code == 0
    assert out.strip() == "1"


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert __version__ in out
    assert "base-conversion" in out


def test_error_exit_code_and_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = _run(capsys, "gg", "16", "10")
    assert code == 1
    assert "错误" in err
    assert "g" in err


def test_base_out_of_range_error(capsys: pytest.CaptureFixture[str]) -> None:
    code, _, err = _run(capsys, "1", "99", "10")
    assert code == 1
    assert "base must be" in err
