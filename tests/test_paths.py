# tests/test_paths.py

from __future__ import annotations

from pathlib import Path

from password_engine.runtime.runtime import AppPaths
from password_engine.utils.paths.paths import (
    _xdg_home,
    ensure_dirs,
    ensure_optional_dirs,
    get_app_paths,
)


def test_xdg_home_returns_env_value(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg-data"))

    result = _xdg_home("XDG_DATA_HOME", Path("/fallback"))

    assert result == tmp_path / "xdg-data"


def test_xdg_home_returns_fallback_for_empty_value(monkeypatch):
    fallback = Path("/fallback")
    monkeypatch.setenv("XDG_DATA_HOME", "   ")

    result = _xdg_home("XDG_DATA_HOME", fallback)

    assert result == fallback


def test_get_app_paths_uses_xdg_env_vars(monkeypatch, tmp_path: Path):
    from password_engine.identity import IDENTITY
    import password_engine.utils.paths.paths as paths_module

    monkeypatch.setattr(paths_module.Path, "home", staticmethod(lambda: tmp_path / "home"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data-home"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state-home"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache-home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config-home"))

    result = get_app_paths()

    assert result.data_dir == tmp_path / "data-home" / IDENTITY.app_name
    assert result.state_dir == tmp_path / "state-home" / IDENTITY.app_name
    assert result.cache_dir == tmp_path / "cache-home" / IDENTITY.app_name
    assert result.tmp_dir == tmp_path / "cache-home" / IDENTITY.app_name / "tmp"
    assert result.config_dir == tmp_path / "config-home" / IDENTITY.app_name


def test_get_app_paths_uses_default_locations_when_env_missing(monkeypatch, tmp_path: Path):
    from password_engine.identity import IDENTITY
    import password_engine.utils.paths.paths as paths_module

    fake_home = tmp_path / "home"
    monkeypatch.setattr(paths_module.Path, "home", staticmethod(lambda: fake_home))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

    result = get_app_paths()

    assert result.data_dir == fake_home / ".local" / "share" / IDENTITY.app_name
    assert result.state_dir == fake_home / ".local" / "state" / IDENTITY.app_name
    assert result.cache_dir == fake_home / ".cache" / IDENTITY.app_name
    assert result.tmp_dir == fake_home / ".cache" / IDENTITY.app_name / "tmp"
    assert result.config_dir == fake_home / ".config" / IDENTITY.app_name


def test_ensure_dirs_creates_core_directories(tmp_path: Path):
    paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )

    ensure_dirs(paths)

    assert paths.data_dir.is_dir()
    assert paths.state_dir.is_dir()
    assert paths.cache_dir.is_dir()
    assert paths.tmp_dir.is_dir()
    assert paths.config_dir.is_dir()
    assert not paths.logs_dir.exists()


def test_ensure_optional_dirs_creates_logs_dir_when_enabled(tmp_path: Path):
    paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    paths.state_dir.mkdir(parents=True, exist_ok=True)

    ensure_optional_dirs(paths, logs_dir=True)

    assert paths.logs_dir.is_dir()


def test_ensure_optional_dirs_does_nothing_when_disabled(tmp_path: Path):
    paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    paths.state_dir.mkdir(parents=True, exist_ok=True)

    ensure_optional_dirs(paths, logs_dir=False)

    assert not paths.logs_dir.exists()
