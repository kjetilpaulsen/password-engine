import logging
import sys

# FIX: change project name for imports
from password_engine.entrypoints import cli_main, api_main
from password_engine.identity import IDENTITY
from password_engine.utils.logging.setuplogging import setup_basic_logging



def main() -> int:
    """
    Starts basic logging and decides between entrypoints.
    """
    setup_basic_logging()
    logger = logging.getLogger(__name__)

    argv = sys.argv[1:]
    if not argv:
        logger.warning("Usage: %s [cli|api] ...", IDENTITY.package_name)
        return 2
    
    mode, *rest = argv

    if mode == "cli":
        return cli_main(rest)

    if mode == "api":
        return api_main(rest)

    logger.warning("Unknown entrypoint: %s", mode)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
