# tests/test_cli.py

from __future__ import annotations

from pathlib import Path

from password_engine.events.events import EvtLog, EvtResult
from password_engine.runtime.runtime import (
    AppPaths,
    CFGDataBase,
    CFGDev,
    CFGLogging,
    CFGMisc,
    MetaInfo,
    Runtime,
)
from password_engine.runtime.runtimeoverrides import RuntimeOverrides


def _make_runtime(tmp_path: Path) -> Runtime:
    paths = AppPaths(
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        cache_dir=tmp_path / "cache",
        tmp_dir=tmp_path / "cache" / "tmp",
        config_dir=tmp_path / "config",
    )
    return Runtime(
        meta=MetaInfo(
            app_name="password-engine",
            app_version="1.2.3",
            app_description="test app",
        ),
        paths=paths,
        dev=CFGDev(dev_mode=True, dry_run=False),
        log=CFGLogging(),
        db=CFGDataBase(),
        misc=CFGMisc(build_config=False),
    )


def test_cli_success_path(monkeypatch, tmp_path: Path):
    from password_engine.cli import cli as cli_module
    from password_engine.commands.frontendcommandinput import FrontendCommandInput
    from password_engine.commands.commands import CmdDisplayVersion

    runtime = _make_runtime(tmp_path)
    calls: dict[str, object] = {}

    frontend_inputs = (
        FrontendCommandInput(name="version", options={"uppercase": True}),
    )
    overrides = RuntimeOverrides(dev_mode=True)

    def fake_cli_parser(argv):
        calls["cli_parser"] = argv
        return frontend_inputs, overrides

    def fake_build_commands(inputs):
        calls["build_commands"] = inputs
        return (CmdDisplayVersion(uppercase=True),)

    def fake_build_runtime(received_overrides):
        calls["build_runtime"] = received_overrides
        return runtime

    def fake_setup_logging(appname, paths, log):
        calls["setup_logging"] = (appname, paths, log)

    def fake_log_runtime(received_runtime):
        calls["log_runtime"] = received_runtime

    class FakeApp:
        def __init__(self, meta, dev, db, paths) -> None:
            calls["app_init"] = (meta, dev, db, paths)

        def run(self, commands):
            calls["app_run"] = commands
            return iter(
                [
                    EvtLog(message="starting"),
                    EvtResult(
                        command_name="DisplayVersion",
                        payload={"version": "V1.2.3"},
                    ),
                ]
            )

    class FakeCliEventHandler:
        def __init__(self) -> None:
            self.seen = []
            calls["handler_created"] = True

        def handle(self, evt) -> None:
            self.seen.append(evt)
            calls.setdefault("handled_events", []).append(evt)

    monkeypatch.setattr(cli_module, "cli_parser", fake_cli_parser)
    monkeypatch.setattr(cli_module, "build_commands", fake_build_commands)
    monkeypatch.setattr(cli_module, "build_runtime", fake_build_runtime)
    monkeypatch.setattr(cli_module, "setup_logging", fake_setup_logging)
    monkeypatch.setattr(cli_module, "log_runtime", fake_log_runtime)
    monkeypatch.setattr(cli_module, "App", FakeApp)
    monkeypatch.setattr(cli_module, "CliEventHandler", FakeCliEventHandler)

    result = cli_module.cli(["version", "--uppercase"])

    assert result == 0
    assert calls["cli_parser"] == ["version", "--uppercase"]
    assert calls["build_commands"] == frontend_inputs
    assert calls["build_runtime"] == overrides
    assert calls["setup_logging"] == (
        cli_module.IDENTITY.logger_name,
        runtime.paths,
        runtime.log,
    )
    assert calls["log_runtime"] == runtime
    assert calls["app_init"] == (runtime.meta, runtime.dev, runtime.db, runtime.paths)
    assert calls["handled_events"] == [
        EvtLog(message="starting"),
        EvtResult(command_name="DisplayVersion", payload={"version": "V1.2.3"}),
    ]


def test_cli_returns_130_on_keyboard_interrupt(monkeypatch):
    from password_engine.cli import cli as cli_module

    def fake_cli_parser(_argv):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli_module, "cli_parser", fake_cli_parser)

    result = cli_module.cli(["version"])

    assert result == 130


def test_cli_returns_1_on_unhandled_exception(monkeypatch):
    from password_engine.cli import cli as cli_module

    def fake_cli_parser(_argv):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "cli_parser", fake_cli_parser)

    result = cli_module.cli(["version"])

    assert result == 1
