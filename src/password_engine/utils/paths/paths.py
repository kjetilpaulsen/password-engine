from __future__ import annotations

import os
from pathlib import Path

# FIX: change project name for imports
from password_engine.identity import IDENTITY
from password_engine.runtime.runtime import AppPaths


def _xdg_home(var: str, fallback: Path) -> Path:
    """
    Resolve an XDG base directory from an environment variable.

    The function checks whether the given environment variable is set
    and non-empty. If so, the value is converted to a `Path` and used.
    Otherwise, the provided fallback path is returned.

    Args:
        var: Name of the environment variable representing an XDG
            base directory (for example `XDG_DATA_HOME`).
        fallback: Default path to use if the environment variable
            is not set or empty.

    Returns:
        Path: The resolved path from the environment variable, or
        the fallback path if the variable is not defined.
    """
    v = os.getenv(var)
    return Path(v) if v and v.strip() else fallback

def get_app_paths() -> AppPaths:
    """
    Resolve application-specific filesystem paths following the XDG specification.

    The function determines base directories using the XDG environment
    variables if they are defined. Otherwise, standard fallback locations
    under the user's home directory are used.

    Default locations:

        data:   ~/.local/share/<app_name>
        state:  ~/.local/state/<app_name>
        cache:  ~/.cache/<app_name>
        tmp:    ~/.cache/<app_name>/tmp
        config: ~/.config/<app_name>

    In container environments (for example Docker), the XDG environment
    variables may be mapped to container volumes such as `/data`, `/state`,
    `/cache`, or `/config`. In that case the resulting directories become
    `/data/<app_name>`, `/state/<app_name>`, etc.

    Returns:
        AppPaths: A dataclass containing the resolved application
        directory paths.
    """

    home = Path.home()

    data_home = _xdg_home("XDG_DATA_HOME", home / ".local" / "share")
    state_home = _xdg_home("XDG_STATE_HOME", home / ".local" / "state")
    cache_home = _xdg_home("XDG_CACHE_HOME", home / ".cache")
    config_home = _xdg_home("XDG_CONFIG_HOME", home / ".config")

    data_dir = data_home / IDENTITY.app_name
    state_dir = state_home / IDENTITY.app_name
    cache_dir = cache_home / IDENTITY.app_name
    config_dir = config_home / IDENTITY.app_name

    tmp_dir = cache_dir / "tmp"


    return AppPaths(data_dir, state_dir, cache_dir, tmp_dir, config_dir)

def ensure_dirs(paths: AppPaths) -> None:
    """
    Ensure that the application's core directories exist.

    This function creates the standard XDG directories used by the
    application if they do not already exist. Existing directories
    are left unchanged.

    Args:
        paths: The resolved application path container.

    Returns:
        None
    """
    for p in (paths.data_dir, paths.state_dir, paths.cache_dir, paths.tmp_dir, paths.config_dir):
        p.mkdir(parents=True, exist_ok=True)

def ensure_optional_dirs(paths: AppPaths,
                logs_dir: bool = False,
                ) -> None:
    """
    Create optional application directories if enabled.

    Some directories are only required when specific runtime features
    are enabled (for example file-based logging). This function creates
    those directories when requested.

    Args:
        paths: The resolved application path container.
        logs_dir: If `True`, ensure that the log directory exists.

    Returns:
        None
    """
    if logs_dir:
        paths.logs_dir.mkdir(parents=True, exist_ok = True)
