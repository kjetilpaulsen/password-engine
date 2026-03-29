from __future__ import annotations

import logging

# FIX: change project name for imports
from password_engine.cli.clieventhandler import CliEventHandler
from password_engine.commands.buildcommands import build_commands
from password_engine.commands.commands import Command
from password_engine.events.events import EvtError
from password_engine.identity import IDENTITY
from password_engine.runtime.runtime import Runtime
from password_engine.utils.logging.setuplogging import setup_logging
from password_engine.runtime.buildruntime import build_runtime
from password_engine.cli.cliparser import cli_parser
from password_engine.app import App
from password_engine.runtime.logruntime import log_runtime

logger = logging.getLogger(__name__)

def cli(argv: list[str] | None = None) -> int:
    """
    Execute the command-line interface entrypoint.

    This function parses CLI arguments, builds the application runtime,
    configures logging, and executes the requested commands through the
    application engine.

    The CLI follows this execution flow:

        1. Parse command-line arguments into structured command inputs.
        2. Convert command inputs into executable command objects.
        3. Build the runtime configuration (paths, logging, database, etc.).
        4. Configure logging according to runtime settings.
        5. Run the application command pipeline and handle emitted events.

    Args:
        argv: Optional list of CLI arguments. If `None`, arguments are read
            from `sys.argv` by the CLI parser. This parameter is primarily
            useful for testing or programmatic invocation.

    Returns:
        int: Process exit code.

            - `0` if execution completed successfully.
            - `130` if execution was interrupted by the user (Ctrl+C).
            - `1` if an unexpected fatal error occurred.
    """
    logger.info("--STARTING CLI--")
    try:
        frontendinputcommands, overrides= cli_parser(argv)

        queue: list[Command] = [build_commands(cmd) for cmd in frontendinputcommands]
        runtime: Runtime = build_runtime(overrides)

        setup_logging(IDENTITY.logger_name,
                      runtime.paths,
                      runtime.log)
        log_runtime(runtime)

        app = App(runtime.meta, runtime.dev, runtime.db, runtime.paths)
        evt_handler = CliEventHandler()

        logger.debug("Starting queue with: %s", queue)
        while queue:
            cmd, *queue = queue
            logger.debug("Sending command")
            for evt in app.run(cmd):
                if isinstance(evt, EvtError) and evt.fatal:
                    logger.error("Fatal error in command %s; %s", cmd.cmd_id, evt.message)
                    break

                logger.debug("Yielded, cli about to handle event")
                new_cmd = evt_handler.handle(evt)
                if isinstance(new_cmd, Command):
                    queue.append(new_cmd)

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        return 130
    except Exception:
        logger.exception("---FATAL ERROR---")
        return 1
    return 0

