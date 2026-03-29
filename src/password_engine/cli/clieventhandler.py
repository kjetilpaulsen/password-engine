from __future__ import annotations

import logging
from typing import Callable

# FIX: change project name for imports
from password_engine.commands.commands import Command, CmdConfirmPassword
from password_engine.events.events import (
    Event,
    EvtConfirmPassword,
    EvtStarted,
    EvtFinished,
    EvtProgress,
    EvtLogMessage,
    EvtError,
    EvtResult,
    EvtRequestInput,

)

logger = logging.getLogger(__name__)

class CliEventHandler:
    """
    Handle application events for the CLI frontend.

    The `CliEventHandler` receives events produced by the application
    execution pipeline and converts them into CLI-visible output such
    as log messages, progress indicators, or printed results.

    Each event type corresponds to a specific frontend behavior. This
    keeps the CLI presentation layer separated from the core application
    logic.

    Event types currently handled include:

        - `EvtMessage`: informational log messages
        - `EvtProgress`: progress updates for long-running tasks
        - `EvtError`: error reporting
        - `EvtResult`: command execution results

    Unrecognized event types are logged as warnings.
    FIX: update docstring
    """
    def __init__(self) -> None:
        logger.info("--INITIALIZING CLIEVENTHANDLER--")
        self._events: dict[type[Event], Callable] ={
            EvtStarted: lambda evt: self._handle_evtstarted(evt),
            EvtFinished: lambda evt: self._handle_evtfinished(evt),
            EvtProgress: lambda evt: self._handle_evtprogress(evt),
            EvtLogMessage: lambda evt: self._handle_evtlogmessage(evt),
            EvtError: lambda evt: self._handle_evterror(evt),
            EvtResult: lambda evt: self._handle_evtresult(evt),
            EvtConfirmPassword: lambda evt: self._handle_evtrequestinput(evt),

        }

    def handle(self, evt: Event) -> Command | None:
        """
        Process an application event and convert it into CLI output.

        The handler inspects the event type and performs the appropriate
        action for the CLI environment. Typical actions include logging
        informational messages, displaying progress updates, reporting
        errors, or printing command results.

        Args:
            evt: An application event emitted by `App.run()`.

        Returns:
            None
        FIX: update docstring
        """
        event = self._events.get(type(evt))
        if event is None:
            logger.error(f"Event not found in _events: {type(evt).__name__}")
        return event(evt)

    def _handle_evtstarted(self, evt) -> None:
        logger.info("name=%s, UUID=%s", evt.cmd_name, evt.cmd_id)
        return None

    def _handle_evtfinished(self, evt) -> None:
        logger.info("name=%s, UUID=%s, ok=%s, summary=%s", evt.cmd_name, evt.cmd_id, evt.ok, evt.summary)
        return None

    def _handle_evtprogress(self, evt) -> None:
        return None

    def _handle_evtlogmessage(self, evt) -> None:
        LOG_LEVEL_MAP = {
            "debug": logger.debug,
            "info": logger.info,
            "warning": logger.warning,
        }
        LOG_LEVEL_MAP.get(evt.level, logger.info)(evt.message)
        return None

    def _handle_evterror(self, evt) -> None:
        logger.error("code=%s, message=%s, fatal=%s, details=%s", evt.code, evt.message, evt.fatal, evt.details)
        return None

    def _handle_evtresult(self, evt) -> None:
        logger.info("result_type=%s, payload=%s, is_final=%s", evt.result_type, evt.payload, evt.is_final)
        return None

    def _handle_evtrequestinput(self, evt) -> Command:
        # Needs to be handled
        # Currently hardcoded confirmpassword
        print(f"{evt.prompt}")
        inp = input("Answer: ")
        while inp not in evt.choices:
            inp = input("Try again: ")
        if inp == evt.choices[0]:
            tag = input("Tag: ")
            site_username = input("Site_username: ")
            site_email = input("Site email: ")
            site_url = input("Site url: ")
            return CmdConfirmPassword(
                cmd_id=evt.cmd_id,
                password=evt.password,
                session=evt.session,
                tag=tag,
                site_username=site_username,
                site_email=site_email,
                site_url=site_url,
            )
        elif inp == evt.choices[1]:
            return evt.original_cmd
