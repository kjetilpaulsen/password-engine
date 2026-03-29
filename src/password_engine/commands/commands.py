from dataclasses import dataclass

class Command:
    """
    Base class for one-shot app commands.
    """
    cmd_id: str # UUID

@dataclass(frozen=True)
class CmdDisplayVersion(Command):
    uppercase: bool = False

@dataclass(frozen=True)
class CmdGeneratePassword(Command):
    lowercase: bool = False
    uppercase: bool = False
    numbers: bool = False
    specials: bool = False
    password_length: int = 12

@dataclass(frozen=True)
class CmdListPasswords(Command): ...

@dataclass(frozen=True)
class CmdCreateUser(Command): ...

@dataclass(frozen=True)
class CmdConfirmPassword(Command):
    password: str
