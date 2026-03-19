from password_engine.commands.commands import CmdDisplayVersion
from password_engine.handlers.displayversionhandler import DisplayVersionHandler
from password_engine.runtime.runtime import MetaInfo
from password_engine.events.events import EvtResult


def test_display_version_handler_returns_evtresult():
    cmd = CmdDisplayVersion(
        uppercase=False,

    )
    meta = MetaInfo(
        app_name="password-engine",
        app_version="1.2.3",
        app_description="test app",
    )

    handler = DisplayVersionHandler(cmd, meta)

    events = list(handler.handle())

    assert len(events) == 1
    assert isinstance(events[0], EvtResult)
    assert events[0].command_name == "DisplayVersion"
    assert events[0].payload == {"version": "v1.2.3"}
