from __future__ import annotations
import logging
from typing import Iterator

# FIX: change project name for imports
from password_engine.auth.auth import AuthService, AuthenticatedSession
from password_engine.commands.commands import Command, CmdConfirmPassword, CmdGeneratePassword
from password_engine.db.repo import PasswordRepo
from password_engine.encryption.crypto import encrypt_secret
from password_engine.events.events import Event, EvtConfirmPassword, EvtLogMessage, EvtRequestInput, EvtResult
from password_engine.generator.passwordgenerator import PasswordGenerator
from password_engine.handlers.commandhandler import CommandHandler
from password_engine.runtime.runtime import MetaInfo

logger = logging.getLogger(__name__)

class StorePasswordHandler(CommandHandler):
    """
    Command handler responsible for executing the `CmdDisplayVersion` command.

    Handlers encapsulate the execution logic for a specific command type.
    Each handler receives the command instance together with the runtime
    dependencies it requires and produces a stream of `Event` objects
    describing the execution result.

    This handler resolves and returns the application's current version.
    """
    def __init__(self, cmd: CmdConfirmPassword, password_repo: PasswordRepo):
        self.cmd = cmd
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
        yield from self._store_password()


    def _store_password(self) -> Iterator[Event]:
        encrypted = encrypt_secret(
            plaintext=self.cmd.password,
            key=self.cmd.session.vault_key,
        )
        self.password_repo.insert_vault_entry(
            owner_user_id=self.cmd.session.user_id,
            tag=self.cmd.tag,
            site_username=self.cmd.site_username,
            site_email=self.cmd.site_email,
            site_url=self.cmd.site_url,
            encrypted_password=encrypted.ciphertext,
            encryption_nonce=encrypted.nonce,
            encryption_key_version=encrypted.key_version,
        )
        yield EvtLogMessage(cmd_id=self.cmd.cmd_id, level="info", message="Password generated and stored")
