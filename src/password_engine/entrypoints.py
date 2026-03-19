import sys

import uvicorn

# FIX: change project name for imports
from password_engine.cli.cli import cli
from password_engine.identity import IDENTITY

def cli_main(argv: list[str]) -> int:
    """
    Execute the CLI entrypoint.

    This function acts as a thin wrapper around the main CLI implementation,
    allowing the top-level application entrypoint to delegate execution based
    on the selected frontend mode.

    Args:
        argv: Command-line arguments passed to the CLI.

    Returns:
        int: Exit code returned by the CLI execution.
    """
    return cli(argv)

def api_main(argv: list[str]) -> int:
    """
    Start the API server using Uvicorn.

    This function parses a small set of API-specific command-line arguments
    and launches the FastAPI application through the Uvicorn ASGI server.

    Supported arguments include:

        --host   Set the bind address for the API server.
        --port   Set the listening port for the API server.
        --reload Enable automatic server reload for development.

    Args:
        argv: Command-line arguments passed to the API entrypoint.

    Returns:
        int: Exit code. Returns `0` if the server was started successfully,
        or `2` if invalid arguments were supplied.
    """
    host = "127.0.0.1"
    port = 8010
    reload = False

    i = 0
    while i < len(argv):
        arg = argv[i]

        if arg == "--reload":
            reload = True
            i += 1
            continue

        if arg == "--host":
            i += 1
            host = argv[i]
            i += 1
            continue

        if arg == "--port":
            i += 1
            port = int(argv[i])
            i += 1
            continue

        print(f"Unknown api arg {arg}", file=sys.stderr)
        return 2

    uvicorn.run(
        f"{IDENTITY.package_name}.api.api:api",
        host=host,
        port=port,
        reload=reload,
    )
    return 0

