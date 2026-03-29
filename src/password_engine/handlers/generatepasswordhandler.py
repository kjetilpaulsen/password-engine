from __future__ import annotations
import logging
from typing import Iterator

# FIX: change project name for imports
from password_engine.auth.auth import AuthService
from password_engine.commands.commands import CmdDisplayVersion, CmdGeneratePassword
from password_engine.db.repo import PasswordRepo
from password_engine.encryption.crypto import encrypt_secret
from password_engine.events.events import Event, EvtConfirmPassword, EvtLogMessage, EvtRequestInput, EvtResult
from password_engine.generator.passwordgenerator import PasswordGenerator
from password_engine.handlers.commandhandler import CommandHandler
from password_engine.runtime.runtime import MetaInfo

logger = logging.getLogger(__name__)

class GeneratePasswordHandler(CommandHandler):
    """
    Command handler responsible for executing the `CmdDisplayVersion` command.

    Handlers encapsulate the execution logic for a specific command type.
    Each handler receives the command instance together with the runtime
    dependencies it requires and produces a stream of `Event` objects
    describing the execution result.

    This handler resolves and returns the application's current version.
    """
    def __init__(self, cmd: CmdGeneratePassword, auth_service: AuthService, password_repo: PasswordRepo):
        self.cmd = cmd
        self.auth_service=auth_service
        self.password_repo=password_repo

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
        yield from self._generate_password()

    def _generate_password(self) -> Iterator[Event]:
        session = self.auth_service.authenticate_user(
            username=self.cmd.username,
            master_password=self.cmd.password,
        )
        pwdgntr = PasswordGenerator(
            self.cmd.uppercase,
            self.cmd.lowercase,
            self.cmd.numbers,
            self.cmd.specials,
            self.cmd.password_length,
            )
        pwd = pwdgntr.generate()
        yield EvtConfirmPassword(
            cmd_id=self.cmd.cmd_id,
            request_id = "0", #FIX this to be uuid
            prompt = f"Is the password accepted: {pwd}\n(y/n)",
            input_kind = "confirm",
            field_name = "confirm",
            required = True,
            choices = ["y", "n"],
            original_cmd = self.cmd,
            password = pwd,
            session = session,
        )
