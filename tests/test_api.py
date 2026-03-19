# tests/test_api.py

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from password_engine.api.api import (
    api,
    APIRunRequest,
    APICommand,
    _build_command_inputs,
    _event_to_api,
)
from password_engine.events.events import Event, EvtError, EvtLog, EvtProgress, EvtResult
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
        dev=CFGDev(dev_mode=False, dry_run=False),
        log=CFGLogging(),
        db=CFGDataBase(),
        misc=CFGMisc(build_config=False),
    )


def test_build_command_inputs_converts_api_request():
    req = APIRunRequest(
        commands=[
            APICommand(name="version", options={"uppercase": True}),
        ]
    )

    result = _build_command_inputs(req)

    assert len(result) == 1
    assert result[0].name == "version"
    assert result[0].options == {"uppercase": True}


@pytest.mark.parametrize(
    ("evt", "expected_type", "expected_data"),
    [
        (EvtLog(message="hello"), "log", {"message": "hello"}),
        (
            EvtProgress(current=1, total=5, message="working"),
            "progress",
            {"current": 1, "total": 5, "message": "working"},
        ),
        (
            EvtError(message="boom", fatal=False),
            "error",
            {"message": "boom", "fatal": False},
        ),
        (
            EvtResult(command_name="DisplayVersion", payload={"version": "v1.2.3"}),
            "result",
            {"command_name": "DisplayVersion", "payload": {"version": "v1.2.3"}},
        ),
    ],
)
def test_event_to_api_known_events(evt: Event, expected_type: str, expected_data: dict[str, object]):
    result = _event_to_api(evt)

    assert result.type == expected_type
    assert result.data == expected_data


def test_event_to_api_unknown_event():
    class UnknownEvent(Event):
        pass

    result = _event_to_api(UnknownEvent())

    assert result.type == "unknown"
    assert result.data == {"event_class": "UnknownEvent"}


def test_run_endpoint_returns_500_when_runtime_not_initialized(monkeypatch: pytest.MonkeyPatch):
    from password_engine.api import api as api_module

    monkeypatch.setattr(api_module, "_RUNTIME", None)

    client = TestClient(api)
    response = client.post(
        "/run",
        json={"commands": [{"name": "version", "options": {}}]},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Runtime not initialized"}


def test_run_endpoint_returns_events(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from password_engine.api import api as api_module

    runtime = _make_runtime(tmp_path)
    monkeypatch.setattr(api_module, "_RUNTIME", runtime)

    built_inputs: list[tuple[object, ...]] = []

    def fake_build_commands(command_inputs: tuple[object, ...]) -> tuple[str]:
        built_inputs.append(command_inputs)
        return ("built-command",)

    class FakeApp:
        def __init__(self, meta, dev, db, paths) -> None:
            assert meta == runtime.meta
            assert dev == runtime.dev
            assert db == runtime.db
            assert paths == runtime.paths

        def run(self, commands):
            assert commands == ("built-command",)
            return iter(
                [
                    EvtLog(message="starting"),
                    EvtResult(
                        command_name="DisplayVersion",
                        payload={"version": "v1.2.3"},
                    ),
                ]
            )

    monkeypatch.setattr(api_module, "build_commands", fake_build_commands)
    monkeypatch.setattr(api_module, "App", FakeApp)

    client = TestClient(api)
    response = client.post(
        "/run",
        json={
            "commands": [
                {"name": "version", "options": {"uppercase": False}},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "events": [
            {"type": "log", "data": {"message": "starting"}},
            {
                "type": "result",
                "data": {
                    "command_name": "DisplayVersion",
                    "payload": {"version": "v1.2.3"},
                },
            },
        ],
    }

    assert len(built_inputs) == 1
    assert built_inputs[0][0].name == "version"
    assert built_inputs[0][0].options == {"uppercase": False}


def test_run_endpoint_maps_valueerror_to_400(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from password_engine.api import api as api_module

    monkeypatch.setattr(api_module, "_RUNTIME", _make_runtime(tmp_path))

    def fake_build_commands(_command_inputs):
        raise ValueError("bad command")

    monkeypatch.setattr(api_module, "build_commands", fake_build_commands)

    client = TestClient(api)
    response = client.post(
        "/run",
        json={"commands": [{"name": "version", "options": {}}]},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "bad command"}


def test_run_endpoint_maps_unhandled_exception_to_500(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from password_engine.api import api as api_module

    monkeypatch.setattr(api_module, "_RUNTIME", _make_runtime(tmp_path))
    monkeypatch.setattr(api_module, "build_commands", lambda _command_inputs: ("built-command",))

    class ExplodingApp:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def run(self, _commands):
            raise RuntimeError("unexpected")

    monkeypatch.setattr(api_module, "App", ExplodingApp)

    client = TestClient(api)
    response = client.post(
        "/run",
        json={"commands": [{"name": "version", "options": {}}]},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

def test_health_endpoint_returns_ok():
    client = TestClient(api)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_lifespan_initializes_runtime_and_logging(monkeypatch, tmp_path: Path):
    from password_engine.api import api as api_module

    runtime = _make_runtime(tmp_path)
    calls: dict[str, object] = {}

    monkeypatch.setattr(api_module, "_RUNTIME", None)
    monkeypatch.setattr(api_module, "build_runtime", lambda: runtime)

    def fake_ensure_setup_logging(appname, paths, log) -> None:
        calls["ensure_setup_logging"] = (appname, paths, log)

    def fake_log_runtime(received_runtime) -> None:
        calls["log_runtime"] = received_runtime

    monkeypatch.setattr(api_module, "ensure_setup_logging", fake_ensure_setup_logging)
    monkeypatch.setattr(api_module, "log_runtime", fake_log_runtime)

    async with api_module.lifespan(api_module.api):
        assert api_module._RUNTIME == runtime

    assert calls["ensure_setup_logging"] == (
        api_module.IDENTITY.logger_name,
        runtime.paths,
        runtime.log,
    )
    assert calls["log_runtime"] == runtime
