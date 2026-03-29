from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from password_engine.commands.commands import Command

@dataclass(slots=True, frozen=True)
class Event: 
    cmd_id: str # UUID

@dataclass(slots=True, frozen=True)
class EvtStarted(Event): 
    cmd_name: str # Humanreadable name

@dataclass(slots=True, frozen=True)
class EvtFinished(Event): 
    cmd_name: str # Human readable name
    ok: bool # Finished ok?
    summary: str | None = None # Human readable summary

@dataclass(slots=True, frozen=True)
class EvtProgress(Event):
    current: int | None = None # Current iteration
    total: int | None = None # Number of total iterations
    message: str | None = None # Optional message

@dataclass(slots=True, frozen=True)
class EvtLogMessage(Event):
    level: Literal["debug", "info", "warning"] # Severity
    message: str # Message

@dataclass(slots=True, frozen=True)
class EvtError(Event):
    code: str # Machine readable 
    message: str # Human readable 
    fatal: bool = True # Stop execution?
    details: dict | None = None # Optional for debugging

@dataclass(slots=True, frozen=True)
class EvtResult(Event):
    result_type: str # Semantic type, helps frontend decide how to interpret payload
    payload: object # The resulting data
    is_final: bool = True # If this is the final result of the command

@dataclass(slots=True, frozen=True)
class EvtRequestInput(Event):
    request_id: str # Unique ID for this input request when emitting, used to match to cmd
    prompt: str # Text show to user
    input_kind: Literal["text", "confirm", "select", "secret"] # Expected input by user
    field_name: str # Logical name of the input field, like username or password
    required: bool = True # Required ?
    choices: list[str] | None = None # Relevant for inputs like "select"
    original_cmd: Command | None = None

@dataclass(slots=True, frozen=True)
class EvtConfirmPassword(EvtRequestInput):
    password: str
