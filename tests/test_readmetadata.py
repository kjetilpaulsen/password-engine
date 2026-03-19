# tests/test_readmetadata.py

from __future__ import annotations

from importlib import metadata

from password_engine.runtime.readmetadata import read_metadata


def test_read_metadata_returns_resolved_values(monkeypatch):
    from password_engine.runtime import readmetadata as readmetadata_module

    monkeypatch.setattr(readmetadata_module, "resolve_version", lambda: "2.3.4")
    monkeypatch.setattr(
        readmetadata_module.metadata,
        "metadata",
        lambda dist_name: {"Summary": "Blueprint test app"},
    )

    result = read_metadata()

    assert result.app_name == readmetadata_module.IDENTITY.app_name
    assert result.app_version == "2.3.4"
    assert result.app_description == "Blueprint test app"


def test_read_metadata_falls_back_when_version_lookup_fails(monkeypatch):
    from password_engine.runtime import readmetadata as readmetadata_module

    def raise_version() -> str:
        raise metadata.PackageNotFoundError("missing package")

    monkeypatch.setattr(readmetadata_module, "resolve_version", raise_version)
    monkeypatch.setattr(
        readmetadata_module.metadata,
        "metadata",
        lambda dist_name: {"Summary": "Blueprint test app"},
    )

    result = read_metadata()

    assert result.app_version.startswith("Failed to find version - ")
    assert result.app_description == "Blueprint test app"


def test_read_metadata_falls_back_when_description_lookup_fails(monkeypatch):
    from password_engine.runtime import readmetadata as readmetadata_module

    monkeypatch.setattr(readmetadata_module, "resolve_version", lambda: "2.3.4")

    def raise_metadata(_dist_name: str):
        raise metadata.PackageNotFoundError("no metadata")

    monkeypatch.setattr(readmetadata_module.metadata, "metadata", raise_metadata)

    result = read_metadata()

    assert result.app_version == "2.3.4"
    assert result.app_description.startswith("Failed to find description - ")


def test_read_metadata_falls_back_for_both(monkeypatch):
    from password_engine.runtime import readmetadata as readmetadata_module

    def raise_version() -> str:
        raise metadata.PackageNotFoundError("missing version")

    def raise_metadata(_dist_name: str):
        raise metadata.PackageNotFoundError("missing metadata")

    monkeypatch.setattr(readmetadata_module, "resolve_version", raise_version)
    monkeypatch.setattr(readmetadata_module.metadata, "metadata", raise_metadata)

    result = read_metadata()

    assert result.app_name == readmetadata_module.IDENTITY.app_name
    assert result.app_version.startswith("Failed to find version - ")
    assert result.app_description.startswith("Failed to find description - ")
