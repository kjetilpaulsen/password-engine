# tests/test_logruntime.py

from __future__ import annotations

import logging
from pathlib import Path

from password_engine.runtime.logruntime import log_runtime
from password_engine.runtime.runtime import (
    AppPaths,
    CFGDataBase,
    CFGDev,
    CFGLogging,
    CFGMisc,
    MetaInfo,
    Runtime,
)


def _make_runtime(tmp_path: Path) -> Runtime:
    return Runtime(
        meta=MetaInfo(
            app_name="password-engine",
            app_version="1.2.3",
            app_description="test app",
        ),
        paths=AppPaths(
            data_dir=tmp_path / "data",
            state_dir=tmp_path / "state",
            cache_dir=tmp_path / "cache",
            tmp_dir=tmp_path / "cache" / "tmp",
            config_dir=tmp_path / "config",
        ),
        dev=CFGDev(dev_mode=True, dry_run=False),
        log=CFGLogging(
            log_level=logging.DEBUG,
            console_level=logging.INFO,
            stderr_level=logging.WARNING,
            file_log=True,
            console_log=False,
            stderr_log=True,
        ),
        db=CFGDataBase(
            db_host="db.internal",
            db_name="appdb",
            db_user="alice",
            db_password="super-secret",
            db_port=5432,
        ),
        misc=CFGMisc(build_config=False),
    )


def test_log_runtime_logs_expected_runtime_fields_but_not_password(caplog, tmp_path: Path):
    runtime = _make_runtime(tmp_path)

    with caplog.at_level(logging.INFO):
        log_runtime(runtime)

    text = caplog.text
    assert "--RUNTIME SETTINGS--" in text
    assert "App name: password-engine" in text
    assert "App version: 1.2.3" in text
    assert "App description: test app" in text
    assert "Data directory:" in text
    assert "State directory:" in text
    assert "Cache directory:" in text
    assert "Tmp directory:" in text
    assert "Config directory:" in text
    assert "Logs directory:" in text
    assert "Dev mode: True" in text
    assert "Dry run: False" in text
    assert "Log level:" in text
    assert "Console log level:" in text
    assert "Stderr log level:" in text
    assert "Log to file: True" in text
    assert "Log to console: False" in text
    assert "Log to stderr: True" in text
    assert "super-secret" not in text
    assert "db.internal" not in text
    assert "alice" not in text
