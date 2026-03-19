# tests/test_runtimesettings.py

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from password_engine.runtime.runtimesettings import RuntimeSettings
from password_engine.runtime.runtime import AppPaths


def test_validate_log_level_accepts_named_levels():
    assert RuntimeSettings.validate_log_level("debug") == logging.DEBUG
    assert RuntimeSettings.validate_log_level(" INFO ") == logging.INFO
    assert RuntimeSettings.validate_log_level("warning") == logging.WARNING
    assert RuntimeSettings.validate_log_level("ERROR") == logging.ERROR
    assert RuntimeSettings.validate_log_level("critical") == logging.CRITICAL


def test_validate_log_level_accepts_int_and_numeric_string():
    assert RuntimeSettings.validate_log_level(15) == 15
    assert RuntimeSettings.validate_log_level("20") == 20


def test_validate_log_level_rejects_invalid_value():
    with pytest.raises(ValueError, match="Unsupported log level"):
        RuntimeSettings.validate_log_level("verbose")


def test_resolve_env_file_prefers_cwd_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    dotenv = tmp_path / ".env"
    dotenv.write_text("LOG_LEVEL=INFO\n", encoding="utf-8")

    monkeypatch.setattr(Path, "cwd", staticmethod(lambda: tmp_path))

    xdg_paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    monkeypatch.setattr(
        "password_engine.runtime.runtimesettings.get_app_paths",
        lambda: xdg_paths,
    )

    assert RuntimeSettings.resolve_env_file() == str(dotenv)


def test_resolve_env_file_falls_back_to_xdg_conf(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    monkeypatch.setattr(Path, "cwd", staticmethod(lambda: tmp_path))

    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    conf = config_dir / "password_engine.conf"
    conf.write_text("LOG_LEVEL=INFO\n", encoding="utf-8")

    xdg_paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=config_dir,
    )
    monkeypatch.setattr(
        "password_engine.runtime.runtimesettings.get_app_paths",
        lambda: xdg_paths,
    )

    assert RuntimeSettings.resolve_env_file() == str(conf)


def test_resolve_env_file_returns_none_when_no_files_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    monkeypatch.setattr(Path, "cwd", staticmethod(lambda: tmp_path))

    xdg_paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    monkeypatch.setattr(
        "password_engine.runtime.runtimesettings.get_app_paths",
        lambda: xdg_paths,
    )

    assert RuntimeSettings.resolve_env_file() is None


def test_load_uses_resolved_env_file(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    def fake_resolve_env_file() -> str:
        return "/tmp/fake.env"

    def fake_init(self, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(RuntimeSettings, "resolve_env_file", staticmethod(fake_resolve_env_file))
    monkeypatch.setattr(RuntimeSettings, "__init__", fake_init)

    RuntimeSettings.load(dev_mode=True, db_port=5433)

    assert captured["_env_file"] == "/tmp/fake.env"
    assert captured["dev_mode"] is True
    assert captured["db_port"] == 5433
