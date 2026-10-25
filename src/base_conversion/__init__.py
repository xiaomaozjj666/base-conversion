"""base-conversion — 任意进制（2-62）精确转换库。

核心能力：

- 大整数无精度损失（Python 原生 ``int``）；
- 小数用 ``Fraction`` 精确算术，循环小数用括号循环节表示并可无损往返
  （``1/3`` ↔ ``"0.(3)"``）；
- 2-36 进制大小写不敏感，37-62 大小写敏感（``0-9A-Za-z``）；
- 提供 ``baseconv`` 命令行入口（``pip install`` 后可用）。

快速上手::

    >>> from base_conversion import to_base, to_decimal
    >>> to_base(255, 16)
    'FF'
    >>> to_decimal("0.1", 2)
    Fraction(1, 2)
"""

from base_conversion.converter import (
    BASE_MAX,
    BASE_MIN,
    DIGITS,
    base_to_decimal,
    binary_to_decimal,
    decimal_to_base,
    decimal_to_binary,
    decimal_to_hex,
    hex_to_decimal,
    to_base,
    to_decimal,
)

__version__ = "1.0.0"

__all__ = [
    "BASE_MAX",
    "BASE_MIN",
    "DIGITS",
    "__version__",
    "base_to_decimal",
    "binary_to_decimal",
    "decimal_to_base",
    "decimal_to_binary",
    "decimal_to_hex",
    "hex_to_decimal",
    "to_base",
    "to_decimal",
]
