# tests/test_buildcommands.py

from __future__ import annotations

import pytest

from password_engine.commands.buildcommands import build_commands
from password_engine.commands.commands import CmdDisplayVersion
from password_engine.commands.frontendcommandinput import FrontendCommandInput


def test_build_commands_returns_empty_tuple_for_empty_input():
    result = build_commands(())

    assert result == ()


def test_build_commands_builds_version_command():
    result = build_commands(
        (
            FrontendCommandInput(name="version", options={"uppercase": True}),
        )
    )

    assert result == (CmdDisplayVersion(uppercase=True),)


def test_build_commands_defaults_uppercase_to_false_when_missing():
    result = build_commands(
        (
            FrontendCommandInput(name="version", options={}),
        )
    )

    assert result == (CmdDisplayVersion(uppercase=False),)


def test_build_commands_coerces_truthy_uppercase_value():
    result = build_commands(
        (
            FrontendCommandInput(name="version", options={"uppercase": "yes"}),
        )
    )

    assert result == (CmdDisplayVersion(uppercase=True),)


def test_build_commands_raises_for_unsupported_command():
    with pytest.raises(ValueError, match="Unsupported command input: nope"):
        build_commands((FrontendCommandInput(name="nope", options={}),))
