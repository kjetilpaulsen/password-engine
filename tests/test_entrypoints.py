# tests/test_entrypoints.py

from __future__ import annotations


def test_cli_main_delegates_to_cli(monkeypatch):
    from password_engine import entrypoints

    captured: dict[str, object] = {}

    def fake_cli(argv):
        captured["argv"] = argv
        return 7

    monkeypatch.setattr(entrypoints, "cli", fake_cli)

    result = entrypoints.cli_main(["version", "--uppercase"])

    assert result == 7
    assert captured["argv"] == ["version", "--uppercase"]


def test_api_main_uses_defaults(monkeypatch):
    from password_engine import entrypoints

    captured: dict[str, object] = {}

    def fake_run(app_path: str, host: str, port: int, reload: bool) -> None:
        captured["app_path"] = app_path
        captured["host"] = host
        captured["port"] = port
        captured["reload"] = reload

    monkeypatch.setattr(entrypoints.uvicorn, "run", fake_run)

    result = entrypoints.api_main([])

    assert result == 0
    assert captured == {
        "app_path": f"{entrypoints.IDENTITY.package_name}.api.api:api",
        "host": "127.0.0.1",
        "port": 8010,
        "reload": False,
    }


def test_api_main_parses_host_port_and_reload(monkeypatch):
    from password_engine import entrypoints

    captured: dict[str, object] = {}

    def fake_run(app_path: str, host: str, port: int, reload: bool) -> None:
        captured["app_path"] = app_path
        captured["host"] = host
        captured["port"] = port
        captured["reload"] = reload

    monkeypatch.setattr(entrypoints.uvicorn, "run", fake_run)

    result = entrypoints.api_main(
        ["--host", "0.0.0.0", "--port", "9000", "--reload"]
    )

    assert result == 0
    assert captured == {
        "app_path": f"{entrypoints.IDENTITY.package_name}.api.api:api",
        "host": "0.0.0.0",
        "port": 9000,
        "reload": True,
    }


def test_api_main_returns_2_for_unknown_arg(capsys):
    from password_engine import entrypoints

    result = entrypoints.api_main(["--wat"])

    captured = capsys.readouterr()
    assert result == 2
    assert "Unknown api arg --wat" in captured.err
