# tests/test_utils.py

from __future__ import annotations

from importlib import metadata
import types

from password_engine.utils.utils import compact_dict, load_dotenv_if_present, resolve_version


def test_compact_dict_removes_none_values():
    result = compact_dict(
        {
            "a": 1,
            "b": None,
            "c": False,
            "d": 0,
            "e": "",
        }
    )

    assert result == {
        "a": 1,
        "c": False,
        "d": 0,
        "e": "",
    }


def test_resolve_version_returns_installed_version(monkeypatch):
    from password_engine.utils import utils as utils_module

    monkeypatch.setattr(utils_module.metadata, "version", lambda dist_name: "3.4.5")

    result = resolve_version()

    assert result == "3.4.5"


def test_resolve_version_returns_fallback_on_missing_package(monkeypatch):
    from password_engine.utils import utils as utils_module

    def raise_missing(_dist_name: str) -> str:
        raise metadata.PackageNotFoundError("missing")

    monkeypatch.setattr(utils_module.metadata, "version", raise_missing)

    result = resolve_version()

    assert result == "Cannot resolve version"


def test_load_dotenv_if_present_returns_false_when_python_dotenv_missing(monkeypatch):
    from password_engine.utils import utils as utils_module

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "dotenv":
            raise ImportError
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    result = utils_module.load_dotenv_if_present()

    assert result is False


def test_load_dotenv_if_present_loads_repo_root_env(monkeypatch, tmp_path):
    from password_engine.utils import utils as utils_module

    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    envfile = project_root / ".env"
    envfile.write_text("A=1\n", encoding="utf-8")

    nested_file = project_root / "src" / "password_engine" / "utils" / "utils.py"
    nested_file.parent.mkdir(parents=True, exist_ok=True)
    nested_file.write_text("# placeholder\n", encoding="utf-8")

    calls: dict[str, object] = {}

    fake_dotenv_module = types.SimpleNamespace()

    def fake_load_dotenv(*, dotenv_path, override):
        calls["dotenv_path"] = dotenv_path
        calls["override"] = override

    fake_dotenv_module.load_dotenv = fake_load_dotenv

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "dotenv":
            return fake_dotenv_module
        return original_import(name, *args, **kwargs)

    class FakeResolvedPath(type(utils_module.Path())):
        pass

    monkeypatch.setattr("builtins.__import__", fake_import)
    monkeypatch.setattr(utils_module.Path, "resolve", lambda self: nested_file)

    result = utils_module.load_dotenv_if_present()

    assert result is True
    assert calls["dotenv_path"] == envfile
    assert calls["override"] is False


def test_load_dotenv_if_present_returns_false_when_repo_has_no_env(monkeypatch, tmp_path):
    from password_engine.utils import utils as utils_module

    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    nested_file = project_root / "src" / "password_engine" / "utils" / "utils.py"
    nested_file.parent.mkdir(parents=True, exist_ok=True)
    nested_file.write_text("# placeholder\n", encoding="utf-8")

    fake_dotenv_module = types.SimpleNamespace(load_dotenv=lambda **kwargs: None)

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "dotenv":
            return fake_dotenv_module
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    monkeypatch.setattr(utils_module.Path, "resolve", lambda self: nested_file)

    result = utils_module.load_dotenv_if_present()

    assert result is False
