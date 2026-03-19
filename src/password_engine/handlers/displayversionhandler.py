from __future__ import annotations
import logging
from typing import Iterator

# FIX: change project name for imports
from password_engine.commands.commands import CmdDisplayVersion
from password_engine.events.events import Event, EvtResult
from password_engine.handlers.commandhandler import CommandHandler
from password_engine.runtime.runtime import MetaInfo

logger = logging.getLogger(__name__)

class DisplayVersionHandler(CommandHandler):
    """
    Command handler responsible for executing the `CmdDisplayVersion` command.

    Handlers encapsulate the execution logic for a specific command type.
    Each handler receives the command instance together with the runtime
    dependencies it requires and produces a stream of `Event` objects
    describing the execution result.

    This handler resolves and returns the application's current version.
    """
    def __init__(self, cmd: CmdDisplayVersion, meta: MetaInfo):
        self.cmd = cmd
        self.meta = meta

    def handle(self) -> Iterator[Event]:
        """
        Execute the command and produce events describing the result.

        This method acts as the standard entrypoint for all command
        handlers. It coordinates the execution flow and delegates the
        actual work to helper methods that produce events.

        Handlers emit events using Python generators. This allows the
        application to stream progress updates, intermediate results,
        and final outputs to the frontend.

        Examples of typical event patterns:

            Producing a single result:

                yield EvtResult(...)

            Producing progress updates followed by a result:

                for i in range(total):
                    yield EvtProgress(...)
                yield EvtResult(...)

        Returns:
            Iterator[Event]: A generator yielding events produced during
            command execution.
        """
        logger.info("Handling CmdDisplayVersion ..")
        yield from self.display_version()

    def display_version(self) -> Iterator[Event]:
        """
        Generate an event containing the application's current version.

        The version is retrieved from the application metadata and may
        optionally be transformed depending on the command options.

        Returns:
            Iterator[Event]: A generator yielding a single `EvtResult`
            event containing the resolved version string.
        """
        version = f"v{self.meta.app_version}"
        if self.cmd.uppercase:
            version = version.upper()
        logger.debug("Yielding EvtResult ..")
        yield EvtResult(
            command_name="DisplayVersion",
            payload={"version": version},
            )
