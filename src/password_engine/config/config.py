from __future__ import annotations

# FIX: change project name for imports
from password_engine.identity import IDENTITY
from password_engine.runtime.runtime import AppPaths

CONFIG_TEMPLATE = """########
# Misc #
########

APP_NAME=password-engine
PACKAGE_NAME=password_engine

DEV_MODE=false
DRY_RUN=false
BUILD_CONFIG=false

###########
# Logging #
###########

LOG_LEVEL=debug
CONSOLE_LEVEL=info
STDERR_LEVEL=warning
FILE_LOG=true
CONSOLE_LOG=false
STDERR_LOG=true

############################################
# PostgreSQL connection settings for Local #
############################################

# Local development with peer auth
# DB_HOST=
# DB_NAME=password_engine
# DB_USER=
# DB_PASSWORD=
# DB_PORT=5432

# Docker Compose
DB_HOST=/run/postgresql
DB_NAME=password_engine
DB_USER=password_engine
DB_PASSWORD=replace-me-with-an-actual-password
DB_PORT=5432
HOST_UID=1000
HOST_GID=1000
################################################
# Docker user, docker repo and docker filename #
################################################

# Consider updating this on GitHub Actions aswell
DOCKER_USER=set-user-here
DOCKER_REPO=set-repo-here
DOCKER_TAG=set-tag-here
"""

def build_config_file(paths: AppPaths) -> None:
    """
    Create or overwrite the application's configuration file.

    This function writes a default configuration template to the XDG
    configuration directory resolved by `AppPaths`. If the configuration
    file already exists, it will be overwritten. This allows the command
    to be used to regenerate or reset a broken configuration file.

    The configuration file is written using the application's package
    name as the base filename.

    Args:
        paths: Application path container used to resolve the XDG
            configuration directory where the configuration file
            should be created.

    Returns:
        None
    """
    config_path = paths.config_dir / f"{IDENTITY.package_name}.conf"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with config_path.open("w", encoding="utf-8") as f:
        f.write(CONFIG_TEMPLATE)

