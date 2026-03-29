from dataclasses import dataclass

from password_engine.auth.auth import AuthenticatedSession
@dataclass(frozen=True)
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
    username: str
    password: str
    lowercase: bool = False
    uppercase: bool = False
    numbers: bool = False
    specials: bool = False
    password_length: int = 12

@dataclass(frozen=True)
class CmdListPasswords(Command):
    username: str
    password: str

@dataclass(frozen=True)
class CmdCreateUser(Command):
    username: str
    password: str

@dataclass(frozen=True)
class CmdConfirmPassword(Command):
    password: str
    session: AuthenticatedSession | None = None
    tag: str | None = None
    site_username: str | None = None
    site_email: str | None = None
    site_url: str | None = None
