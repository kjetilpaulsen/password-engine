from __future__ import annotations
from collections.abc import Iterator, Sequence, Callable
import logging

# FIX: change project name for imports
from password_engine.auth.auth import AuthService
from password_engine.commands.commands import CmdConfirmPassword, CmdCreateUser, CmdGeneratePassword, CmdListPasswords, Command, CmdDisplayVersion
from password_engine.events.events import Event, EvtError
from password_engine.handlers.createuserhandler import CreateUserHandler
from password_engine.handlers.displayversionhandler import DisplayVersionHandler
from password_engine.handlers.generatepasswordhandler import GeneratePasswordHandler
from password_engine.handlers.listpasswordshandler import ListPasswordsHandler
from password_engine.handlers.storepasswordhandler import StorePasswordHandler
from password_engine.runtime.runtime import AppPaths, CFGDataBase, CFGDev, MetaInfo
from password_engine.db.connect import connect
from password_engine.db.schema import create_schema
from password_engine.db.repo import PasswordRepo

logger = logging.getLogger(__name__)

class App:
    """
    Core application engine responsible for executing commands.

    The `App` class acts as the central coordinator for the application.
    It owns the runtime configuration and services required to execute
    commands and produce events.

    Commands passed into the application are resolved to handler objects
    which perform the actual work. Handlers emit `Event` objects that
    describe progress, results, or errors. These events are yielded back
    to the caller, allowing different frontends (CLI, API, etc.) to decide
    how to present the results.

    Attributes:
        meta: Application metadata such as name, version, and description.
        dev: Development-related runtime flags.
        db: Database configuration.
        paths: Resolved application filesystem paths.
    """
    def __init__(self, meta: MetaInfo, dev: CFGDev, db: CFGDataBase, paths: AppPaths) -> None:
        """
        Initialize the application runtime.

        The constructor stores the runtime configuration and prepares any
        services required by the application. Service initialization such
        as database connections, caches, or external clients may also be
        performed here.

        Args:
            meta: Application metadata.
            dev: Development configuration flags.
            db: Database configuration settings.
            paths: Resolved filesystem paths used by the application.
        """
        logger.info("--INITIALIZING APP--")
        self.meta = meta
        self.dev = dev
        self.db = db
        self.paths = paths

        # Start services..

        # DB wiring
        conn = connect(self.db)
        create_schema(conn)
        password_repo = PasswordRepo(conn=conn)

        logger.info("DB connection created")

        # Auth service
        auth_service = AuthService(repo=password_repo)

        # Create handlers
        self._handlers: dict[type[Command], Callable] = {
            CmdDisplayVersion: lambda cmd: DisplayVersionHandler(cmd, self.meta).handle(),
            CmdGeneratePassword: lambda cmd: GeneratePasswordHandler(cmd, auth_service, password_repo).handle(),
            CmdListPasswords: lambda cmd: ListPasswordsHandler(cmd, auth_service, password_repo).handle(),
            CmdCreateUser: lambda cmd: CreateUserHandler(cmd, auth_service).handle(),
            CmdConfirmPassword: lambda cmd: StorePasswordHandler(cmd, password_repo).handle(),
        }


    def run(self, cmd: Command) -> Iterator[Event]:
        """
        Execute a sequence of commands and yield resulting events.

        Each command is dispatched to its corresponding handler via
        `_handle_command`. Handlers produce a stream of `Event` objects
        describing the execution results.

        This generator-based design allows frontends to process events
        incrementally instead of waiting for the entire command pipeline
        to complete.

        Args:
            cmds: A sequence of command objects to execute.

        Yields:
            Event: Events produced during command execution.
        """
        logger.debug("Starting run(cmd) ..")
        try:
            handler = self._handlers.get(type(cmd)) 
            if handler is None:
                raise ValueError(f"Command not found in _handlers: {type(cmd).__name__}")
            yield from handler(cmd)
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Unhandled exception while running command %s", type(cmd).__name__)
            yield EvtError(
                cmd_id=cmd.cmd_id, 
                code="UNHANDELED_EXCEPTION", 
                message=str(exc), 
                fatal=True, 
                details={"command_type": type(cmd).__name__,
                },
            )
