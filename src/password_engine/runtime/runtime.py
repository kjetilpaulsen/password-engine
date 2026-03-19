from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

# Immutables
@dataclass(frozen=True)
class MetaInfo:
    app_name: str
    app_version: str
    app_description: str 

@dataclass(frozen=True)
class AppPaths:
    data_dir: Path
    state_dir: Path
    cache_dir: Path
    tmp_dir: Path
    config_dir: Path

    #Add alternative subfolders like so
    @property
    def logs_dir(self) -> Path:
        return self.state_dir / "logs"

@dataclass(frozen=True)
class CFGDev:
    dev_mode: bool = False
    dry_run: bool = False

@dataclass(frozen=True)
class CFGLogging:
    log_level: int = logging.DEBUG
    console_level: int = logging.INFO
    stderr_level: int = logging.WARNING
    file_log: bool = False
    console_log: bool = False
    stderr_log: bool = True

@dataclass(frozen=True)
class CFGDataBase:
    db_host: str | None = None
    db_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_port: int | None = None

@dataclass(frozen=True)
class CFGMisc:
    build_config: bool | None = None

# Consolidation
@dataclass(frozen=True)
class Runtime:
    meta: MetaInfo
    paths: AppPaths
    dev: CFGDev
    log: CFGLogging
    db: CFGDataBase
    misc: CFGMisc
