import logging
import pathlib
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from password_engine.identity import IDENTITY
from password_engine.utils.paths.paths import get_app_paths

class RuntimeSettings(BaseSettings):
    """
    Application runtime settings resolved from overrides, environment
    variables, config files, and defaults.

    The settings model defines the precedence-controlled runtime
    configuration used to construct the application's runtime dataclasses.
    The actual precedence is determined by how values are passed into the
    model together with `BaseSettings` resolution behavior.

    Attributes:
        dev_mode: Enable developer-oriented behavior.
        dry_run: Disable write operations and other side effects.
        log_level: Base logging level, typically used for file logging.
        console_level: Logging level for console output.
        stderr_level: Logging level for stderr output.
        file_log: Enable file-based logging.
        console_log: Enable console logging.
        stderr_log: Enable stderr logging.
        db_host: Database host or socket path.
        db_name: Database name.
        db_user: Database username.
        db_password: Database password.
        db_port: Database port.
        build_config: Whether to create a config file in the XDG config
            directory.
    """
    model_config = SettingsConfigDict(
            #env_file=resolve_env_file(),
            env_file_encoding="utf-8",
            extra="ignore",
    )

    #CFGDev
    dev_mode: bool = False
    dry_run: bool = False
    #CFGLogging
    log_level: int = logging.DEBUG
    console_level: int = logging.INFO
    stderr_level: int = logging.WARNING
    file_log: bool = False
    console_log: bool = False
    stderr_log: bool = True
    #CFGDataBase
    db_host: str | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_port: int | None = None
    #CFGMisc
    build_config: bool | None = None

    @staticmethod
    def resolve_env_file() -> str | None:
        """
        Resolve the configuration file path used by `RuntimeSettings`.

        The function first checks for a `.env` file in the current working
        directory. If that file does not exist, it checks for an application
        config file in the XDG config directory. If neither file exists,
        `None` is returned.

        Returns:
            str | None: The path to the `.env` or `.conf` file to use, or
            `None` if no configuration file was found.
        """
        cwd_env = pathlib.Path.cwd() / ".env"
        if cwd_env.exists():
            return str(cwd_env)
        xdg_env = get_app_paths().config_dir / (IDENTITY.logger_name + ".conf")
        if xdg_env.exists():
            return str(xdg_env)
        return None

    @field_validator("log_level", "console_level", "stderr_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> int:
        """
        Validate and normalize a logging level value.

        The validator accepts either an integer logging level or a string
        representation such as `"DEBUG"`, `"INFO"`, `"WARNING"`,
        `"ERROR"`, or `"CRITICAL"`. Numeric strings are also accepted.

        Args:
            value: The raw logging level value to validate.

        Returns:
            int: A normalized integer logging level.

        Raises:
            ValueError: If the value is not a supported logging level.
        """
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            text= value.strip().upper()
            allowed = {
                "DEBUG": logging.DEBUG, 
                "INFO": logging.INFO, 
                "WARNING": logging.WARNING, 
                "ERROR": logging.ERROR, 
                "CRITICAL": logging.CRITICAL,
            }
            if text in allowed:
                return allowed[text]
            if text.isdigit():
                return int(text)
        raise ValueError(f"Unsupported log level: {value}")

    @classmethod
    def load(cls, **overrides: Any) -> RuntimeSettings:
        """
        Create Runtimesettings using resolved env file.
        """
        env_file = cls.resolve_env_file()
        return cls(_env_file=env_file, **overrides)
