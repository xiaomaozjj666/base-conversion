"""CI 构建验证：检查 wheel 内容完整性（包模块 + 入口齐全）。"""

from __future__ import annotations

import glob
import sys
import zipfile


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    dist_dir = args[0] if args else "dist"
    wheels = sorted(glob.glob(f"{dist_dir}/*.whl"))
    if not wheels:
        print(f"no wheel found in {dist_dir}/")
        return 1
    names = zipfile.ZipFile(wheels[0]).namelist()
    required = (
        "base_conversion/__init__.py",
        "base_conversion/converter.py",
        "base_conversion/cli.py",
    )
    missing = [r for r in required if r not in names]
    if missing:
        print(f"wheel missing: {missing}")
        return 1
    print(f"wheel contents OK: {wheels[0]} ({len(names)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
