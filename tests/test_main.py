# tests/test_main.py

from __future__ import annotations


def test_main_returns_2_when_no_args(monkeypatch):
    from password_engine import __main__ as main_module

    monkeypatch.setattr(main_module, "setup_basic_logging", lambda: None)
    monkeypatch.setattr(main_module.sys, "argv", ["prog"])

    result = main_module.main()

    assert result == 2


def test_main_dispatches_to_cli(monkeypatch):
    from password_engine import __main__ as main_module

    monkeypatch.setattr(main_module, "setup_basic_logging", lambda: None)
    monkeypatch.setattr(main_module.sys, "argv", ["prog", "cli", "version", "--uppercase"])
    monkeypatch.setattr(main_module, "cli_main", lambda argv: 7)

    result = main_module.main()

    assert result == 7


def test_main_dispatches_to_api(monkeypatch):
    from password_engine import __main__ as main_module

    monkeypatch.setattr(main_module, "setup_basic_logging", lambda: None)
    monkeypatch.setattr(main_module.sys, "argv", ["prog", "api", "--port", "9000"])
    monkeypatch.setattr(main_module, "api_main", lambda argv: 9)

    result = main_module.main()

    assert result == 9


def test_main_returns_2_for_unknown_mode(monkeypatch):
    from password_engine import __main__ as main_module

    monkeypatch.setattr(main_module, "setup_basic_logging", lambda: None)
    monkeypatch.setattr(main_module.sys, "argv", ["prog", "wat"])

    result = main_module.main()

    assert result == 2

# def test_main_module_raises_system_exit_when_run_as_script(monkeypatch):
#     import runpy
#     import pytest
#     from password_engine import __main__ as main_module
#
#     monkeypatch.setattr(main_module, "main", lambda: 17)
#
#     with pytest.raises(SystemExit) as exc_info:
#         runpy.run_module("password_engine.__main__", run_name="__main__")
#
#     assert exc_info.value.code == 17

# def test_main_module_raises_system_exit_when_run_as_script(monkeypatch):
#     import runpy
#     import pytest
#
#     from password_engine import entrypoints
#     from password_engine.utils.logging import setuplogging
#
#     monkeypatch.setattr(setuplogging, "setup_basic_logging", lambda: None)
#     monkeypatch.setattr(entrypoints, "cli_main", lambda argv: 17)
#     monkeypatch.setattr("sys.argv", ["prog", "cli", "version"])
#
#     with pytest.raises(SystemExit) as exc_info:
#         runpy.run_module("password_engine.__main__", run_name="__main__")
#
#     assert exc_info.value.code == 17

def test_main_module_raises_system_exit_when_run_as_script(monkeypatch):
    import runpy
    import sys
    import pytest

    from password_engine import entrypoints
    from password_engine.utils.logging import setuplogging

    monkeypatch.setattr(setuplogging, "setup_basic_logging", lambda: None)
    monkeypatch.setattr(entrypoints, "cli_main", lambda argv: 17)
    monkeypatch.setattr("sys.argv", ["prog", "cli", "version"])

    sys.modules.pop("password_engine.__main__", None)

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("password_engine.__main__", run_name="__main__")

    assert exc_info.value.code == 17
