"""``baseconv`` 命令行入口。

用法::

    baseconv NUMBER [FROM_BASE] [TO_BASE]     # 位置参数式（基数默认 10）
    baseconv -n NUMBER -f FROM -t TO           # 选项式（负数输入推荐）
    baseconv -- -123 10 2                     # ``--`` 分隔符式

输出即目标进制表示：整数为数字串，精确小数为有限位或括号循环节
（``0.(3)`` 表示 1/3 的十进制循环展开）。
"""

from __future__ import annotations

import argparse
import re
import sys

from base_conversion import __version__
from base_conversion.converter import to_base, to_decimal

# 形如 "-123" / "+12.5" 的首个位置参数会被 argparse 误认成选项；
# 自动在其前插入 ``--`` 分隔符。
_LEADING_NUMBER = re.compile(r"^[-+][0-9]")


def _normalize_argv(argv: list[str]) -> list[str]:
    """首参数是带符号数字时插入 ``--``，避免被当作选项解析。"""
    if argv and _LEADING_NUMBER.match(argv[0]) and argv[0] not in ("-h", "--help"):
        return ["--", *argv]
    return argv


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="baseconv",
        description=(
            "任意进制（2-62）精确转换：大整数无损、小数用分数精确表示、循环小数输出括号循环节。"
        ),
        epilog=(
            "示例:\n"
            "  baseconv 255 10 16        # → FF\n"
            "  baseconv -- -123 10 2     # → -1111011（负数用 -- 分隔）\n"
            "  baseconv -n 0.1 -f 2 -t 10  # → 0.5（二进制小数精确转十进制）"
        ),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"base-conversion {__version__}",
        help="显示版本并退出",
    )
    parser.add_argument(
        "number",
        nargs="?",
        help="待转换的数字（源进制下的字符串形式；也可用 -n 提供）",
    )
    parser.add_argument("from_base", nargs="?", type=int, default=10, help="源进制（默认 10）")
    parser.add_argument("to_base_pos", nargs="?", type=int, default=10, help="目标进制（默认 10）")
    parser.add_argument("-n", "--number", dest="number_opt", help="数字（选项式，负数推荐）")
    parser.add_argument(
        "-f", "--from-base", dest="from_base_opt", type=int, help="源进制（选项式，优先于位置）"
    )
    parser.add_argument(
        "-t", "--to-base", dest="to_base_opt", type=int, help="目标进制（选项式，优先于位置）"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：返回 0 成功 / 1 转换错误 / 2 用法错误（argparse 自带）。"""
    args_list = sys.argv[1:] if argv is None else list(argv)
    args_list = _normalize_argv(args_list)
    parser = build_parser()
    ns = parser.parse_args(args_list)

    number = ns.number_opt if ns.number_opt is not None else ns.number
    from_base = ns.from_base_opt if ns.from_base_opt is not None else ns.from_base
    target_base = ns.to_base_opt if ns.to_base_opt is not None else ns.to_base_pos

    if number is None:
        parser.error("必须提供待转换的数字（位置参数或 -n）")

    try:
        value = to_decimal(number, from_base)
        print(to_base(value, target_base))
    except (ValueError, TypeError) as exc:
        print(f"baseconv: 错误: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
