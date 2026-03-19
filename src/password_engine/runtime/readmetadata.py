from importlib import metadata

# FIX: change project name for imports
from password_engine.identity import IDENTITY
from password_engine.runtime.runtime import MetaInfo
from password_engine.utils.utils import resolve_version



def read_metadata() -> MetaInfo: 
    """
    Read application metadata and return it as a `MetaInfo` object.

    The function resolves the application version and description from
    installed package metadata. If metadata cannot be found, fallback
    strings are used instead.

    Returns:
        MetaInfo: A metadata object containing the application name,
        version, and description.
    """
    try:
        app_version = resolve_version()
    except metadata.PackageNotFoundError as e:
        app_version = f"Failed to find version - {e}"

    try:
        meta = metadata.metadata(IDENTITY.dist_name)
        app_description = str(meta.get("Summary"))
    except metadata.PackageNotFoundError as e:
        app_description = f"Failed to find description - {e}"

    return MetaInfo(
        app_name=IDENTITY.app_name,
        app_version=app_version,
        app_description=app_description)
