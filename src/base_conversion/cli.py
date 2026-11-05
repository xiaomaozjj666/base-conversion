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

# 带符号输入可能以数字、字母、小数点或循环括号开头，如 -123、-FF、-.5。
_SIGNED_NUMBER = re.compile(r"^[-+](?=[0-9A-Za-z.(])")
_OPTION_FLAGS = frozenset(
    {"-h", "--help", "-V", "--version", "-n", "--number", "-f", "--from-base", "-t", "--to-base"}
)


def _is_signed_number(value: str) -> bool:
    """判断参数是否形如带符号数字，而非 CLI 自身的选项。"""
    return value not in _OPTION_FLAGS and _SIGNED_NUMBER.match(value) is not None


def _normalize_argv(argv: list[str]) -> list[str]:
    """避免 argparse 将带符号数字误判为选项。

    ``-n``/``--number`` 后的带符号值改写为 ``--number=VALUE``；首个位置参数
    为带符号值时保留原有兼容行为，自动在其前插入 ``--``。
    """
    normalized: list[str] = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--":
            normalized.extend(argv[index:])
            break
        if (
            arg in ("-n", "--number")
            and index + 1 < len(argv)
            and _is_signed_number(argv[index + 1])
        ):
            normalized.append(f"--number={argv[index + 1]}")
            index += 2
            continue
        normalized.append(arg)
        index += 1

    if normalized and _is_signed_number(normalized[0]):
        return ["--", *normalized]
    return normalized


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="baseconv",
        description=(
            "任意进制（2-62）精确转换：大整数无损、小数用分数精确表示、循环小数输出括号循环节。"
        ),
        epilog=(
            "示例:\n"
            "  baseconv 255 10 16           # → FF\n"
            "  baseconv -- -FF 16 10        # → -255（位置参数负数用 -- 分隔）\n"
            "  baseconv -n -FF -f 16 -t 10  # → -255（-n 可直接接收负数值）\n"
            "  baseconv -n 0.1 -f 2 -t 10   # → 0.5（二进制小数精确转十进制）"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        help="待转换的数字（源进制字符串；负数可用 -- 分隔或用 -n 提供）",
    )
    parser.add_argument("from_base", nargs="?", type=int, default=10, help="源进制（默认 10）")
    parser.add_argument("to_base_pos", nargs="?", type=int, default=10, help="目标进制（默认 10）")
    parser.add_argument(
        "-n", "--number", dest="number_opt", help="数字（可直接接收 -FF、-0.1 等负数值）"
    )
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
