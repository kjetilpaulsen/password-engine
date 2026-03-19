# tests/test_clieventhandler.py

from __future__ import annotations

import logging

from password_engine.cli.clieventhandler import CliEventHandler
from password_engine.events.events import Event, EvtError, EvtLog, EvtProgress, EvtResult


def test_cli_event_handler_logs_evtlog(caplog):
    handler = CliEventHandler()

    with caplog.at_level(logging.INFO):
        handler.handle(EvtLog(message="hello world"))

    assert "hello world" in caplog.text


def test_cli_event_handler_logs_evterror(caplog):
    handler = CliEventHandler()

    with caplog.at_level(logging.ERROR):
        handler.handle(EvtError(message="boom", fatal=False))

    assert "boom - Fatal=False" in caplog.text


def test_cli_event_handler_prints_evtresult(capsys):
    handler = CliEventHandler()

    handler.handle(
        EvtResult(
            command_name="DisplayVersion",
            payload={"version": "v1.2.3"},
        )
    )

    captured = capsys.readouterr()
    assert captured.out.strip() == "DisplayVersion - {'version': 'v1.2.3'}"


def test_cli_event_handler_ignores_evtprogress(capsys, caplog):
    handler = CliEventHandler()

    with caplog.at_level(logging.INFO):
        handler.handle(EvtProgress(current=1, total=10, message="working"))

    captured = capsys.readouterr()
    assert captured.out == ""
    assert caplog.text == ""


def test_cli_event_handler_warns_for_unknown_event(caplog):
    handler = CliEventHandler()

    class UnknownEvent(Event):
        pass

    with caplog.at_level(logging.WARNING):
        handler.handle(UnknownEvent())

    assert "Unhandled event type: UnknownEvent" in caplog.text
