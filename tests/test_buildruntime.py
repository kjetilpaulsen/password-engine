# tests/test_buildruntime.py

from __future__ import annotations

import logging
from pathlib import Path

from password_engine.runtime.buildruntime import build_runtime
from password_engine.runtime.runtime import AppPaths, MetaInfo
from password_engine.runtime.runtimeoverrides import RuntimeOverrides


class FakeSettings:
    def __init__(
        self,
        *,
        dev_mode: bool,
        dry_run: bool,
        log_level: int,
        console_level: int,
        stderr_level: int,
        file_log: bool,
        console_log: bool,
        stderr_log: bool,
        db_host: str | None,
        db_name: str | None,
        db_user: str | None,
        db_password: str | None,
        db_port: int | None,
        build_config: bool | None,
    ) -> None:
        self.dev_mode = dev_mode
        self.dry_run = dry_run
        self.log_level = log_level
        self.console_level = console_level
        self.stderr_level = stderr_level
        self.file_log = file_log
        self.console_log = console_log
        self.stderr_log = stderr_log
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.build_config = build_config


def test_build_runtime_uses_defaults_and_calls_path_helpers(
    monkeypatch,
    tmp_path: Path,
):
    paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    meta = MetaInfo(
        app_name="password-engine",
        app_version="1.2.3",
        app_description="test app",
    )

    called: dict[str, object] = {}

    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.read_metadata",
        lambda: meta,
    )
    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.get_app_paths",
        lambda: paths,
    )

    def fake_ensure_dirs(received_paths):
        called["ensure_dirs"] = received_paths

    def fake_ensure_optional_dirs(received_paths, logs_dir):
        called["ensure_optional_dirs"] = (received_paths, logs_dir)

    def fake_load(**kwargs):
        called["load_kwargs"] = kwargs
        return FakeSettings(
            dev_mode=False,
            dry_run=False,
            log_level=logging.DEBUG,
            console_level=logging.INFO,
            stderr_level=logging.WARNING,
            file_log=False,
            console_log=False,
            stderr_log=True,
            db_host=None,
            db_name=None,
            db_user=None,
            db_password=None,
            db_port=None,
            build_config=False,
        )

    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.ensure_dirs",
        fake_ensure_dirs,
    )
    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.ensure_optional_dirs",
        fake_ensure_optional_dirs,
    )
    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.RuntimeSettings.load",
        fake_load,
    )

    runtime = build_runtime(None)

    assert runtime.meta == meta
    assert runtime.paths == paths
    assert runtime.dev.dev_mode is False
    assert runtime.dev.dry_run is False

    assert runtime.log.log_level == logging.DEBUG
    assert runtime.log.console_level == logging.INFO
    assert runtime.log.file_log is False
    assert runtime.log.console_log is False
    assert runtime.log.stderr_log is True

    assert runtime.db.db_host == "/run/postgresql"
    assert runtime.db.db_name == "password_engine"
    assert runtime.db.db_user is None
    assert runtime.db.db_password is None
    assert runtime.db.db_port == 5432

    assert runtime.misc.build_config is False

    assert called["load_kwargs"] == {}
    assert called["ensure_dirs"] == paths
    assert called["ensure_optional_dirs"] == (paths, False)


def test_build_runtime_applies_overrides_and_builds_config(
    monkeypatch,
    tmp_path: Path,
):
    paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    meta = MetaInfo(
        app_name="password-engine",
        app_version="9.9.9",
        app_description="test app",
    )

    called: dict[str, object] = {}

    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.read_metadata",
        lambda: meta,
    )
    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.get_app_paths",
        lambda: paths,
    )

    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.ensure_dirs",
        lambda received_paths: called.setdefault("ensure_dirs", received_paths),
    )
    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.ensure_optional_dirs",
        lambda received_paths, logs_dir: called.setdefault(
            "ensure_optional_dirs", (received_paths, logs_dir)
        ),
    )
    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.build_config_file",
        lambda received_paths: called.setdefault("build_config_file", received_paths),
    )

    def fake_load(**kwargs):
        called["load_kwargs"] = kwargs
        return FakeSettings(
            dev_mode=True,
            dry_run=True,
            log_level=logging.ERROR,
            console_level=logging.CRITICAL,
            stderr_level=logging.WARNING,
            file_log=True,
            console_log=True,
            stderr_log=False,
            db_host="db.internal",
            db_name="custom_db",
            db_user="alice",
            db_password="secret",
            db_port=5544,
            build_config=True,
        )

    monkeypatch.setattr(
        "password_engine.runtime.buildruntime.RuntimeSettings.load",
        fake_load,
    )

    overrides = RuntimeOverrides(
        dev_mode=True,
        dry_run=True,
        build_config=True,
        log_level="ERROR",
        console_level="CRITICAL",
        stderr_level="WARNING",
        file_log=True,
        console_log=True,
        stderr_log=False,
        db_host="db.internal",
        db_name="custom_db",
        db_user="alice",
        db_password="secret",
        db_port=5544,
    )

    runtime = build_runtime(overrides)

    assert runtime.dev.dev_mode is True
    assert runtime.dev.dry_run is True

    assert runtime.log.log_level == logging.ERROR
    assert runtime.log.console_level == logging.CRITICAL
    assert runtime.log.stderr_level == logging.WARNING
    assert runtime.log.file_log is True
    assert runtime.log.console_log is True
    assert runtime.log.stderr_log is False

    assert runtime.db.db_host == "db.internal"
    assert runtime.db.db_name == "custom_db"
    assert runtime.db.db_user == "alice"
    assert runtime.db.db_password == "secret"
    assert runtime.db.db_port == 5544

    assert runtime.misc.build_config is True

    assert called["load_kwargs"] == {
        "dev_mode": True,
        "dry_run": True,
        "build_config": True,
        "log_level": "ERROR",
        "console_level": "CRITICAL",
        "stderr_level": "WARNING",
        "file_log": True,
        "console_log": True,
        "stderr_log": False,
        "db_host": "db.internal",
        "db_name": "custom_db",
        "db_user": "alice",
        "db_password": "secret",
        "db_port": 5544,
    }
    assert called["ensure_dirs"] == paths
    assert called["ensure_optional_dirs"] == (paths, True)
    assert called["build_config_file"] == paths
