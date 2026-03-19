from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeOverrides:
    dev_mode: bool | None = None
    dry_run: bool | None = None
    build_config: bool | None = None
    log_level: str | int | None = None
    console_level: str | int | None = None
    stderr_level: str | int | None = None
    file_log: bool | None = None
    console_log: bool | None = None
    stderr_log: bool | None = None
    db_host: str | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_port: int | None = None
