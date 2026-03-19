# tests/test_config.py

from __future__ import annotations

from pathlib import Path

from password_engine.config.config import CONFIG_TEMPLATE, build_config_file
from password_engine.runtime.runtime import AppPaths


def _make_paths(tmp_path: Path) -> AppPaths:
    return AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )


def test_build_config_file_creates_expected_file(tmp_path: Path):
    from password_engine.identity import IDENTITY

    paths = _make_paths(tmp_path)

    build_config_file(paths)

    config_path = paths.config_dir / f"{IDENTITY.package_name}.conf"
    assert config_path.exists()
    assert config_path.read_text(encoding="utf-8") == CONFIG_TEMPLATE


def test_build_config_file_overwrites_existing_file(tmp_path: Path):
    from password_engine.identity import IDENTITY

    paths = _make_paths(tmp_path)
    config_path = paths.config_dir / f"{IDENTITY.package_name}.conf"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("old content", encoding="utf-8")

    build_config_file(paths)

    assert config_path.read_text(encoding="utf-8") == CONFIG_TEMPLATE
