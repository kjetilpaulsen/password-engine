import logging

# FIX: change project name for imports
from password_engine.runtime.runtime import Runtime

logger = logging.getLogger(__name__)

def log_runtime(runtime: Runtime) -> None:
    """
    Log the resolved runtime configuration.

    This function emits informational log entries describing the active
    runtime configuration for the current application run. The purpose is
    to make it easier to inspect the environment and settings used during
    execution.

    Sensitive values such as database passwords or other secrets are
    intentionally excluded from the log output.

    Args:
        runtime: The fully constructed runtime object containing metadata,
            filesystem paths, development flags, logging configuration,
            and other runtime settings.

    Returns:
        None
    """
    logger.info("--RUNTIME SETTINGS--")
    logger.info("App name: %s", runtime.meta.app_name)
    logger.info("App version: %s", runtime.meta.app_version)
    logger.info("App description: %s", runtime.meta.app_description)
    logger.info("Data directory: %s", runtime.paths.data_dir)
    logger.info("State directory: %s", runtime.paths.state_dir)
    logger.info("Cache directory: %s", runtime.paths.cache_dir)
    logger.info("Tmp directory: %s", runtime.paths.tmp_dir)
    logger.info("Config directory: %s", runtime.paths.config_dir)
    logger.info("Logs directory: %s", runtime.paths.logs_dir)
    logger.info("Dev mode: %s", runtime.dev.dev_mode)
    logger.info("Dry run: %s", runtime.dev.dry_run)
    logger.info("Log level: %s", runtime.log.log_level)
    logger.info("Console log level: %s", runtime.log.console_level)
    logger.info("Stderr log level: %s", runtime.log.stderr_level)
    logger.info("Log to file: %s", runtime.log.file_log)
    logger.info("Log to console: %s", runtime.log.console_log)
    logger.info("Log to stderr: %s", runtime.log.stderr_log)

