from __future__ import annotations

import logging
from typing import Iterator

from password_engine.auth.auth import AuthService
from password_engine.commands.commands import CmdCreateUser
from password_engine.events.events import Event, EvtLog
from password_engine.handlers.commandhandler import CommandHandler

logger = logging.getLogger(__name__)


class CreateUserHandler(CommandHandler):
    """
    Command handler responsible for executing the `CmdDisplayVersion` command.

    Handlers encapsulate the execution logic for a specific command type.
    Each handler receives the command instance together with the runtime
    dependencies it requires and produces a stream of `Event` objects
    describing the execution result.

    This handler resolves and returns the application's current version.
    """

    def __init__(self, cmd: CmdCreateUser, auth_service: AuthService):
        self.cmd = cmd
        self.auth_service = auth_service

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
        logger.info("Handling CmdCreateUser ..")
        yield from self._create_user()

    def _input_username(self) -> str:
        return input("Username: ")

    def _input_password(self) -> str:
        return input("Password: ")

    def _input_confirm_password(self) -> str:
        return input("Confirm password: ")

    def _create_user(self) -> Iterator[Event]:
        username = self._input_username()
        password = self._input_password()
        confirm_password = self._input_confirm_password()

        if password != confirm_password:
            raise ValueError("Passwords do not match")

        self.auth_service.register_user(
            username=username,
            master_password=password,
        )

        yield EvtLog(message="User created")
