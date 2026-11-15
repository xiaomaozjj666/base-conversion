"""分发包内容回归测试。"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

from base_conversion import __version__


def _build_wheel(tmp_path: Path) -> Path:
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(tmp_path),
            str(project_root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = list(tmp_path.glob("*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def test_public_version_matches_distribution_metadata(tmp_path: Path) -> None:
    with zipfile.ZipFile(_build_wheel(tmp_path)) as wheel:
        metadata_name = next(
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = wheel.read(metadata_name).decode("utf-8")
    assert f"Version: {__version__}" in metadata.splitlines()


def test_wheel_contains_package_modules_and_pep561_marker(tmp_path: Path) -> None:
    """实际构建 wheel，防止包模块或 PEP 561 标记在发布物中丢失。"""
    with zipfile.ZipFile(_build_wheel(tmp_path)) as wheel:
        names = set(wheel.namelist())
    required = {
        "base_conversion/__init__.py",
        "base_conversion/cli.py",
        "base_conversion/converter.py",
        "base_conversion/py.typed",
    }
    assert required <= names
