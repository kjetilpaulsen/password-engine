# tests/test_setuplogging.py

from __future__ import annotations

import logging
from logging import FileHandler, StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path

from password_engine.runtime.runtime import AppPaths, CFGLogging
from password_engine.utils.logging import setuplogging


def _make_paths(tmp_path: Path) -> AppPaths:
    logs_dir = tmp_path / "state" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )


def test_setup_basic_logging_configures_root_logger():
    root_logger = logging.getLogger()
    old_handlers = list(root_logger.handlers)
    old_level = root_logger.level

    try:
        setuplogging.setup_basic_logging()

        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) >= 1
    finally:
        root_logger.handlers.clear()
        for handler in old_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(old_level)


def test_setup_logging_calls_configure_and_sets_initialized(monkeypatch, tmp_path: Path):
    paths = _make_paths(tmp_path)
    log_cfg = CFGLogging()
    captured: dict[str, object] = {}

    def fake_configure(appname, received_paths, received_log) -> None:
        captured["args"] = (appname, received_paths, received_log)

    monkeypatch.setattr(setuplogging, "_configure_logging", fake_configure)
    monkeypatch.setattr(setuplogging, "_LOGGING_INITIALIZED", False)

    setuplogging.setup_logging("password_engine", paths, log_cfg)

    assert captured["args"] == ("password_engine", paths, log_cfg)
    assert setuplogging._LOGGING_INITIALIZED is True


def test_ensure_setup_logging_only_runs_once(monkeypatch, tmp_path: Path):
    paths = _make_paths(tmp_path)
    log_cfg = CFGLogging()
    calls: list[tuple[str, AppPaths, CFGLogging]] = []

    def fake_configure(appname, received_paths, received_log) -> None:
        calls.append((appname, received_paths, received_log))

    monkeypatch.setattr(setuplogging, "_configure_logging", fake_configure)
    monkeypatch.setattr(setuplogging, "_LOGGING_INITIALIZED", False)

    setuplogging.ensure_setup_logging("password_engine", paths, log_cfg)
    setuplogging.ensure_setup_logging("password_engine", paths, log_cfg)

    assert calls == [("password_engine", paths, log_cfg)]
    assert setuplogging._LOGGING_INITIALIZED is True


def test_configure_logging_adds_stderr_handler_only(tmp_path: Path):
    paths = _make_paths(tmp_path)
    log_cfg = CFGLogging(
        log_level=logging.DEBUG,
        console_level=logging.INFO,
        stderr_level=logging.ERROR,
        file_log=False,
        console_log=False,
        stderr_log=True,
    )

    root_logger = logging.getLogger()
    old_handlers = list(root_logger.handlers)
    old_level = root_logger.level

    try:
        setuplogging._configure_logging("password_engine", paths, log_cfg)

        handlers = list(root_logger.handlers)
        assert root_logger.level == logging.DEBUG
        assert len(handlers) == 1
        assert isinstance(handlers[0], StreamHandler)
        assert handlers[0].level == logging.ERROR
    finally:
        for handler in list(root_logger.handlers):
            handler.close()
        root_logger.handlers.clear()
        for handler in old_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(old_level)


def test_configure_logging_adds_file_and_console_handlers(tmp_path: Path):
    paths = _make_paths(tmp_path)
    log_cfg = CFGLogging(
        log_level=logging.WARNING,
        console_level=logging.INFO,
        stderr_level=logging.ERROR,
        file_log=True,
        console_log=True,
        stderr_log=False,
    )

    root_logger = logging.getLogger()
    old_handlers = list(root_logger.handlers)
    old_level = root_logger.level

    try:
        setuplogging._configure_logging("password_engine", paths, log_cfg)

        handlers = list(root_logger.handlers)

        assert root_logger.level == logging.DEBUG
        assert len(handlers) == 3
        assert any(isinstance(h, RotatingFileHandler) for h in handlers)
        assert any(
            isinstance(h, FileHandler) and not isinstance(h, RotatingFileHandler)
            for h in handlers
        )
        assert any(isinstance(h, StreamHandler) for h in handlers)
    finally:
        for handler in list(root_logger.handlers):
            handler.close()
        root_logger.handlers.clear()
        for handler in old_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(old_level)
