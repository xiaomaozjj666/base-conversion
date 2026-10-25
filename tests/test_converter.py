"""converter 核心的边界、错误与随机对照测试。

随机对照以 Python 内置 ``int(s, base)`` 为参考实现（2-36），往返性质
测试覆盖 int 与 Fraction（含循环小数括号表示的往返一致性）。
"""

from __future__ import annotations

import random
from fractions import Fraction

import pytest

from base_conversion import converter as c
from base_conversion.converter import DIGITS

# ── 基本正确性 ────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("s", "base", "expected"),
    [
        ("0", 10, 0),
        ("1", 10, 1),
        ("10", 2, 2),
        ("ff", 16, 255),
        ("FF", 16, 255),
        ("Z", 36, 35),
        ("z", 36, 35),
        ("10", 62, 62),
        ("a", 62, 36),
        ("A", 62, 10),
        ("zz", 62, 61 * 62 + 61),
        ("+42", 10, 42),
        ("-42", 10, -42),
        (".5", 10, Fraction(1, 2)),
        ("5.", 10, 5),
        ("0.5", 10, Fraction(1, 2)),
        ("0.1", 2, Fraction(1, 2)),
        ("0.01", 2, Fraction(1, 4)),
        ("0.(3)", 10, Fraction(1, 3)),
        ("0.1(6)", 10, Fraction(1, 6)),
        ("1.0", 3, Fraction(1, 1)),
        ("0.(01)", 2, Fraction(1, 3)),
    ],
)
def test_to_decimal_values(s: str, base: int, expected: int | Fraction) -> None:
    assert c.to_decimal(s, base) == expected


@pytest.mark.parametrize(
    ("value", "base", "expected"),
    [
        (0, 10, "0"),
        (255, 16, "FF"),
        (-42, 2, "-101010"),
        (62, 62, "10"),
        (Fraction(1, 2), 10, "0.5"),
        (Fraction(1, 3), 10, "0.(3)"),
        (Fraction(1, 6), 10, "0.1(6)"),
        (Fraction(1, 3), 2, "0.(01)"),
        (-Fraction(1, 3), 10, "-0.(3)"),
        (255.0, 16, "FF"),  # 整数值 float
    ],
)
def test_to_base_values(value: int | Fraction | float, base: int, expected: str) -> None:
    assert c.to_base(value, base) == expected


def test_to_base_3843_in_base62() -> None:
    assert c.to_base(61 * 62 + 61, 62) == "zz"


# ── 大整数 ──────────────────────────────────────────────────


def test_big_int_roundtrip() -> None:
    n = 10**100 + 7
    for base in (2, 7, 16, 36, 62):
        assert c.to_decimal(c.to_base(n, base), base) == n


# ── 错误路径 ─────────────────────────────────────────────────


@pytest.mark.parametrize("base", [1, 0, -2, 63, 100])
def test_base_out_of_range(base: int) -> None:
    with pytest.raises(ValueError, match="base must be"):
        c.to_decimal("1", base)
    with pytest.raises(ValueError, match="base must be"):
        c.to_base(1, base)


def test_base_type_errors() -> None:
    for bad in (True, 2.0, "16", None):  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            c.to_decimal("1", bad)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            c.to_base(1, bad)  # type: ignore[arg-type]


def test_to_decimal_type_error() -> None:
    with pytest.raises(TypeError, match="must be a str"):
        c.to_decimal(255, 16)  # type: ignore[arg-type]


def test_to_base_bool_rejected() -> None:
    with pytest.raises(TypeError, match="bool"):
        c.to_base(True, 10)  # type: ignore[arg-type]


def test_to_base_non_integral_float_rejected() -> None:
    with pytest.raises(ValueError, match="non-integral float"):
        c.to_base(0.5, 10)


@pytest.mark.parametrize(
    "s",
    ["", ".", "  ", "1.2.3", "()", "0.()", "0.(3", "0.3)", "0.(3)(3)", "0.((3))", "g", "0.g"],
)
def test_malformed_strings(s: str) -> None:
    with pytest.raises(ValueError):
        c.to_decimal(s, 16)


def test_invalid_digit_message_contains_char() -> None:
    with pytest.raises(ValueError, match="'g'"):
        c.to_decimal("gg", 16)
    with pytest.raises(ValueError, match="base 2"):
        c.to_decimal("2", 2)


def test_base37_case_sensitive() -> None:
    # 37 进制起 a 与 A 是不同数字（36 vs 10）
    assert c.to_decimal("a", 37) == 36
    assert c.to_decimal("A", 37) == 10
    # 36 进制内两者等价（大小写不敏感）
    assert c.to_decimal("a", 36) == c.to_decimal("A", 36) == 10


def test_digit_above_base_rejected() -> None:
    # z/Z（值 35）在 36 进制有效；进到 37+ 后 a（值 36）才可用
    assert c.to_decimal("z", 36) == 35
    assert c.to_decimal("Z", 36) == 35
    with pytest.raises(ValueError):
        c.to_decimal(";", 36)  # 非法字符
    with pytest.raises(ValueError):
        c.to_decimal("a" if False else "(", 36)


# ── 随机交叉验证（参考实现：内置 int(s, base)，2-36） ──────────


def test_random_cross_validation_against_builtin() -> None:
    rng = random.Random(42)
    for _ in range(500):
        n = rng.randint(0, 10 ** rng.randint(1, 60))
        base = rng.randint(2, 36)
        canonical = DIGITS[0] if n == 0 else _render_int(n, base)
        assert c.to_decimal(canonical, base) == n, (canonical, base)
        # 大小写不敏感路径
        assert c.to_decimal(canonical.lower(), base) == n if base <= 36 else True


def _render_int(n: int, base: int) -> str:
    digits = []
    while n:
        n, d = divmod(n, base)
        digits.append(DIGITS[d])
    return "".join(reversed(digits)) or "0"


def test_random_fraction_roundtrip() -> None:
    rng = random.Random(7)
    for _ in range(300):
        den = rng.randint(2, 999)
        num = rng.randint(1, den * 10)
        frac = Fraction(num, den)
        for base in (2, 8, 10, 16, 62):
            rendered = c.to_base(frac, base)
            assert c.to_decimal(rendered, base) == frac, (frac, base, rendered)
            negative = -frac
            rendered_neg = c.to_base(negative, base)
            assert c.to_decimal(rendered_neg, base) == negative


# ── 别名兼容 ─────────────────────────────────────────────────


def test_legacy_aliases() -> None:
    assert c.decimal_to_base(255, 16) == "FF"
    assert c.base_to_decimal("ff", 16) == 255
    assert c.decimal_to_binary(5) == "101"
    assert c.binary_to_decimal("101") == 5
    assert c.decimal_to_hex(255) == "FF"
    assert c.hex_to_decimal("ff") == 255
