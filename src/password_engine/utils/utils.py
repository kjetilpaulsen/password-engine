from __future__ import annotations

from pathlib import Path
from importlib import metadata
from typing import Any

# FIX: change project name for imports
from password_engine.identity import IDENTITY

def load_dotenv_if_present() -> bool:
    """
    Load a repository-root `.env` file if one exists and `python-dotenv` is
    installed.

    This is intended as a development convenience. In production and container
    environments, real environment variables should be preferred.

    The function walks upward from the current file location until it finds a
    directory containing `pyproject.toml`, treats that directory as the project
    root, and then looks for a `.env` file there. If found, it loads the file
    without overriding existing environment variables.

    Returns:
        int: Returns `1` if a `.env` file was found and loaded, otherwise `0`.
    """
    try:
        from dotenv import load_dotenv #type: ignore[import-not-found]
    except ImportError:
        return False

    here = Path(__file__).resolve()
    for rootpath in (here.parent, *here.parents):
        if (rootpath / "pyproject.toml").exists():
            envfile = rootpath / ".env"
            if envfile.exists():
                load_dotenv(dotenv_path = envfile, override=False)
                return True
            break
    return False

def resolve_version() -> str:
    """
    Resolve the installed package version from project metadata.

    The version is looked up using the package distribution name defined in
    `IDENTITY.dist_name`. If the installed package metadata cannot be found,
    a fallback string is returned instead.

    Returns:
        str: The resolved package version, or `"Cannot resolve version"` if
        package metadata is unavailable.
    """
    try:
        return metadata.version(IDENTITY.dist_name)
    except metadata.PackageNotFoundError:
        return "Cannot resolve version"

def compact_dict(context: dict[str, Any]) -> dict[str, Any]:
    """
    Remove keys whose values that are `None`.

    Args:
        context: A mapping of keys to values.

    Returns:
        dict[str, Any]: A new dictionary containing only keys whose values
        are not `None`.
    """
    return {k: v for k, v in context.items() if v is not None}
