from dataclasses import dataclass

class Command:
    """
    Base class for one-shot app commands.
    """

@dataclass(frozen=True)
class CmdDisplayVersion(Command):
    uppercase: bool = False

@dataclass(frozen=True)
class CmdGeneratePassword(Command):
    lowercase: bool = False
    uppercase: bool = False
    numbers: bool = False
    specials: bool = False

@dataclass(frozen=True)
class CmdListPasswords(Command): ...

@dataclass(frozen=True)
class CmdCreateUser(Command): ...
