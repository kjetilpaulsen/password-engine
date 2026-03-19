from __future__ import annotations

import logging
from dataclasses import asdict

# FIX: change project name for imports
from password_engine.config.config import build_config_file
from password_engine.runtime.runtimeoverrides import RuntimeOverrides
from password_engine.runtime.readmetadata import read_metadata
from password_engine.runtime.runtime import (
    CFGDataBase,
    CFGDev,
    CFGLogging,
    CFGMisc,
    Runtime,
)
from password_engine.runtime.runtimesettings import RuntimeSettings
from password_engine.utils.paths.paths import (
    ensure_dirs,
    ensure_optional_dirs,
    get_app_paths,
)
from password_engine.utils.utils import compact_dict

logger = logging.getLogger(__name__)

def build_runtime(rto: RuntimeOverrides | None = None) -> Runtime:
    """
    Build the full application runtime from resolved configuration.

    The runtime is assembled from metadata, XDG paths, optional override
    values, environment/config settings, and defaults. The resulting
    `Runtime` object contains the grouped dataclasses used by the rest of
    the application.

    Configuration precedence is:

        overrides > environment > `.env` / `.conf` > defaults

    Args:
        rto: Optional runtime overrides, typically provided by the CLI.
            If omitted, runtime settings are resolved entirely from
            environment/config/default sources.

    Returns:
        Runtime: The fully constructed runtime-settings object.
    """
    logger.info("Building runtime ..")

    # Build metadata
    meta = read_metadata()

    # Build paths
    paths = get_app_paths()
    ensure_dirs(paths)

    # Build settings
    clean_rto = compact_dict(asdict(rto)) if rto is not None else {}
    settings = RuntimeSettings.load(**clean_rto)

    # Build config
    if settings.build_config:
        logger.info("Building config file ..")
        build_config_file(paths)

    # Build optional paths
    ensure_optional_dirs(paths, logs_dir=settings.file_log)

    dev = CFGDev(
        dev_mode = settings.dev_mode,
        dry_run = settings.dry_run
    )

    log = CFGLogging(
        log_level = settings.log_level,
        console_level = settings.console_level,
        stderr_level = settings.stderr_level,
        file_log = settings.file_log,
        console_log = settings.console_log,
        stderr_log = settings.stderr_log,
    )

    db = CFGDataBase(
        db_host = settings.db_host or "/run/postgresql",
        db_name = settings.db_name or meta.app_name.replace("-","_"),
        db_user = settings.db_user,
        db_password = settings.db_password,
        db_port = settings.db_port or 5432,
    )
    misc=CFGMisc(
        build_config = settings.build_config,
    )

    return Runtime(
        meta=meta,
        paths=paths,
        dev=dev,
        log=log,
        db=db,
        misc=misc,
    )
