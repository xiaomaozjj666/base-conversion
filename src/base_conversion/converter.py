"""Core conversion routines for the base-conversion library.

Convert numbers between arbitrary bases from 2 to 62 with exact
integer/Fraction arithmetic, including repeating-digit notation such as
``"0.(3)"`` for 1/3 in base 10.
"""

from __future__ import annotations

from fractions import Fraction

__all__ = [
    "BASE_MAX",
    "BASE_MIN",
    "DIGITS",
    "base_to_decimal",
    "binary_to_decimal",
    "decimal_to_base",
    "decimal_to_binary",
    "decimal_to_hex",
    "hex_to_decimal",
    "to_base",
    "to_decimal",
]

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

BASE_MIN = 2
BASE_MAX = 62

# Digit value lookup: character -> value (0..61).
_DIGIT_VALUES = {ch: i for i, ch in enumerate(DIGITS)}


def _validate_base(base: int) -> None:
    """Validate that *base* is a usable radix.

    Args:
        base: Candidate radix.

    Raises:
        TypeError: If *base* is a ``bool`` or not an ``int``.
        ValueError: If *base* is outside ``[BASE_MIN, BASE_MAX]``.
    """
    if isinstance(base, bool) or not isinstance(base, int):
        raise TypeError(f"base must be an int, got {type(base).__name__}")
    if not BASE_MIN <= base <= BASE_MAX:
        raise ValueError(f"base must be {BASE_MIN}-{BASE_MAX}, got {base}")


def _digit_value(ch: str, base: int) -> int:
    """Return the numeric value of a single digit character.

    For bases 2-36 upper and lower case are both accepted; for bases
    37-62 the alphabetic digits are case sensitive (``'A'`` is 10 and
    ``'a'`` is 36).

    Raises:
        ValueError: If *ch* is not a valid digit in *base*.
    """
    lookup = ch.upper() if base <= 36 else ch
    value = _DIGIT_VALUES.get(lookup)
    if value is None or value >= base:
        raise ValueError(f"invalid character {ch!r} for base {base}")
    return value


def _parse_digit_run(text: str, base: int) -> int:
    """Convert a non-empty run of digits (no sign, no dot) to an int."""
    value = 0
    for ch in text:
        value = value * base + _digit_value(ch, base)
    return value


def to_decimal(s: str, base: int) -> int | Fraction:
    """Parse a string in *base* and return its exact numeric value.

    Accepted grammar (whitespace is not allowed)::

        [sign] digits [ "." digits ] [ "(" digits ")" ]

    * Bases 2-36 are case insensitive; bases 37-62 are case sensitive
      (``'a'`` is worth 36 and only reachable for base >= 37).
    * Either the integer or the fractional digits may be empty, but not
      both (unless a repeating part is present); a bare ``"."`` is an
      error.
    * Repeating digits use parentheses: ``"0.(3)"`` is 1/3 in base 10
      and ``"0.1(6)"`` is 1/6. Empty, nested, or repeated parenthesized
      groups are rejected.

    Args:
        s: The string to parse.
        base: The radix to interpret *s* with (2-62).

    Returns:
        An ``int`` when *s* has no fractional part, otherwise an exact
        ``fractions.Fraction``.

    Raises:
        TypeError: If *s* is not a ``str`` or *base* is not an ``int``.
        ValueError: If *s* is malformed for *base*.
    """
    _validate_base(base)
    if not isinstance(s, str):
        raise TypeError(f"number must be a str, got {type(s).__name__}")

    sign = 1
    body = s
    if body[:1] in ("+", "-"):
        if body[0] == "-":
            sign = -1
        body = body[1:]

    # Extract the repeating (parenthesized) part, if any.
    repeating = ""
    open_count = body.count("(")
    if open_count or body.count(")"):
        if open_count != 1 or body.count(")") != 1:
            raise ValueError(f"multiple or misplaced parentheses in {s!r}")
        open_idx = body.index("(")
        close_idx = body.index(")")
        if close_idx != len(body) - 1 or close_idx < open_idx:
            raise ValueError(f"misplaced parenthesis in {s!r}")
        repeating = body[open_idx + 1 : close_idx]
        if not repeating:
            raise ValueError(f"empty repeating part in {s!r}")
        body = body[:open_idx]

    if body.count(".") > 1:
        raise ValueError(f"more than one decimal point in {s!r}")
    if "." in body:
        int_part, frac_part = body.split(".", 1)
    else:
        int_part, frac_part = body, ""
    if not int_part and not frac_part and not repeating:
        raise ValueError(f"empty or invalid number string {s!r}")

    int_value = _parse_digit_run(int_part, base) if int_part else 0

    if not frac_part and not repeating:
        return sign * int_value

    result = Fraction(int_value)
    if frac_part:
        frac_value = _parse_digit_run(frac_part, base)
        result += Fraction(frac_value, base ** len(frac_part))
    if repeating:
        rep_value = _parse_digit_run(repeating, base)
        n = len(frac_part)
        m = len(repeating)
        # value = int + prefix/base^n + rep/(base^n * (base^m - 1))
        result += Fraction(rep_value, base**n * (base**m - 1))
    return sign * result


def _int_to_digits(n: int, base: int) -> str:
    """Render a non-negative ``int`` as digits in *base* (no sign)."""
    if n == 0:
        return DIGITS[0]
    digits: list[str] = []
    while n:
        n, digit = divmod(n, base)
        digits.append(DIGITS[digit])
    return "".join(reversed(digits))


def _fraction_to_digits(frac: Fraction, base: int) -> str:
    """Render a fractional part (0 <= frac < 1) as digits in *base*.

    Terminating expansions are returned plain (``"5"``); repeating ones
    use parenthesized notation (``"(3)"`` or ``1(6)``), detected by
    memoizing the remainder after each digit.
    """
    digits: list[str] = []
    seen: dict[Fraction, int] = {}
    while frac != 0:
        if frac in seen:
            start = seen[frac]
            prefix = "".join(digits[:start])
            repeating = "".join(digits[start:])
            return f"{prefix}({repeating})"
        seen[frac] = len(digits)
        scaled = frac * base
        digit = scaled.numerator // scaled.denominator
        digits.append(DIGITS[digit])
        frac = scaled - digit
    return "".join(digits)


def to_base(value: int | Fraction | float, base: int) -> str:
    """Render *value* as a string in *base*.

    Args:
        value: An ``int``, an exact ``fractions.Fraction``, or a float
            with an integral value (e.g. ``255.0``). Booleans and
            non-integral floats are rejected.
        base: The target radix (2-62).

    Returns:
        The canonical string for *value* in *base*:

        * uppercase letters for digit values 10-35, lowercase for
          36-61 (so output round-trips case-sensitively in bases 37-62);
        * a leading ``-`` for negative values;
        * repeating notation for non-terminating expansions, e.g.
          ``"0.(3)"`` for 1/3 in base 10.

    Raises:
        TypeError: If *value* is a ``bool`` or of an unsupported type.
        ValueError: If *value* is a non-integral float or *base* is out
            of range.
    """
    _validate_base(base)
    if isinstance(value, bool):
        raise TypeError("value must be an int, Fraction, or integral float, not bool")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(
                f"non-integral float {value!r} is lossy; pass a str or Fraction instead"
            )
        value = int(value)

    if isinstance(value, Fraction):
        sign = "-" if value < 0 else ""
        magnitude = abs(value)
        int_part = magnitude.numerator // magnitude.denominator
        int_str = _int_to_digits(int_part, base)
        frac = magnitude - int_part
        if frac == 0:
            return f"{sign}{int_str}"
        return f"{sign}{int_str}.{_fraction_to_digits(frac, base)}"

    if isinstance(value, int):
        sign = "-" if value < 0 else ""
        return f"{sign}{_int_to_digits(abs(value), base)}"

    raise TypeError(
        f"value must be an int, Fraction, or integral float, got {type(value).__name__}"
    )


# --- Backwards-compatible convenience aliases ---------------------------


def decimal_to_base(value: Fraction | float, base: int) -> str:
    """Alias of :func:`to_base`: render a decimal value in *base*."""
    return to_base(value, base)


def base_to_decimal(s: str, base: int) -> int | Fraction:
    """Alias of :func:`to_decimal`: parse a *base* string to decimal."""
    return to_decimal(s, base)


def decimal_to_binary(value: Fraction | float) -> str:
    """Alias of :func:`to_base` with ``base=2``."""
    return to_base(value, 2)


def binary_to_decimal(s: str) -> int | Fraction:
    """Alias of :func:`to_decimal` with ``base=2``."""
    return to_decimal(s, 2)


def decimal_to_hex(value: Fraction | float) -> str:
    """Alias of :func:`to_base` with ``base=16``."""
    return to_base(value, 16)


def hex_to_decimal(s: str) -> int | Fraction:
    """Alias of :func:`to_decimal` with ``base=16``."""
    return to_decimal(s, 16)
