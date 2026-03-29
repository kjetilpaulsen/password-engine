
from __future__ import annotations
import logging
from typing import Iterator

# FIX: change project name for imports
from password_engine.auth.auth import AuthService
from password_engine.commands.commands import CmdDisplayVersion, CmdGeneratePassword, CmdListPasswords
from password_engine.db.repo import PasswordRepo
from password_engine.encryption.crypto import decrypt_secret, encrypt_secret
from password_engine.events.events import Event, EvtLogMessage, EvtResult
from password_engine.handlers.commandhandler import CommandHandler
from password_engine.runtime.runtime import MetaInfo

logger = logging.getLogger(__name__)

class ListPasswordsHandler(CommandHandler):
    """
    Command handler responsible for executing the `CmdDisplayVersion` command.

    Handlers encapsulate the execution logic for a specific command type.
    Each handler receives the command instance together with the runtime
    dependencies it requires and produces a stream of `Event` objects
    describing the execution result.

    This handler resolves and returns the application's current version.
    """
    def __init__(self, cmd: CmdListPasswords, auth_service: AuthService, password_repo: PasswordRepo):
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
        logger.info(f"Handling {type(self.cmd).__name__}..")
        yield from self._list_passwords()

    def _input_username(self) -> str:
        return input("Username: ")

    def _input_password(self) -> str:
        return input("Password: ")

    def _list_passwords(self) -> Iterator[Event]:
        session = self.auth_service.authenticate_user(
            username=self._input_username(),
            master_password=self._input_password(),
        )

        entries= self.password_repo.list_vault_entries_for_user(session.user_id)

        for entry in entries:
            password = decrypt_secret(
                ciphertext=entry.encrypted_password,
                nonce=entry.encryption_nonce,
                key=session.vault_key,
            )
            print(entry.tag, entry.site_username, entry.site_email, entry.site_url, password)

        yield EvtLogMessage(cmd_id=self.cmd.cmd_id, level="info", message="Password listed")
