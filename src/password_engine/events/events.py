from __future__ import annotations

from dataclasses import dataclass

class Event: 
    pass

@dataclass(frozen=True)
class EvtLog(Event):
    message: str

@dataclass(frozen=True)
class EvtProgress(Event):
    current: int
    total: int
    message: str | None = None

@dataclass(frozen=True)
class EvtError(Event):
    message: str
    fatal: bool = True

@dataclass(frozen=True)
class EvtResult(Event):
    command_name: str
    payload: object
