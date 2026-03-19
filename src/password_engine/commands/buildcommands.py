from __future__ import annotations
import logging
from typing import Callable

# FIX: change project name for imports
from password_engine.commands.commands import CmdCreateUser, CmdGeneratePassword, CmdListPasswords, Command, CmdDisplayVersion
from password_engine.commands.frontendcommandinput import FrontendCommandInput

logger = logging.getLogger(__name__)

def build_commands(cmd_inputs: tuple[FrontendCommandInput, ...]) -> tuple[Command, ...]:
    """
    Convert frontend command inputs into executable command objects.

    This function transforms normalized frontend command descriptions
    (`FrontendCommandInput`) into concrete internal `Command` instances
    that can be executed by the application engine.

    The function acts as the boundary between the frontend layer
    (CLI/API input parsing) and the internal command execution layer.

    Each frontend command name is matched to a corresponding command
    implementation. If an unsupported command name is encountered,
    a `ValueError` is raised.

    Args:
        cmd_inputs: A tuple of frontend command inputs describing the
            commands requested by the user.

    Returns:
        tuple[Command, ...]: A tuple of instantiated command objects
        ready to be executed by `App.run()`.

    Raises:
        ValueError: If an unsupported command name is encountered.
    """

    logger.info("Building commands ..")

    command_builders: dict[str, Callable[[dict[str, object]], Command]] = {
        "version": lambda opts: CmdDisplayVersion(
            uppercase=bool(opts.get("uppercase", False))
        ),
        "generate": lambda opts: CmdGeneratePassword(
            uppercase=bool(opts.get("uppercase", False)),
            lowercase=bool(opts.get("lowercase", False)),
            numbers=bool(opts.get("numbers", False)),
            specials=bool(opts.get("specials", False)),
        ),
        "listpasswords": lambda opts: CmdListPasswords(
        ),
        "createuser": lambda opts: CmdCreateUser(
        ),
    }
    commands: list[Command] = []

    for item in cmd_inputs:
        builder = command_builders.get(item.name)
        if builder is None:
            raise ValueError(f"Unsupported command input: {item.name}")
        commands.append(builder(item.options))
    return tuple(commands)
