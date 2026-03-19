from dataclasses import dataclass, field

@dataclass(frozen=True)
class FrontendCommandInput:
    name: str
    options: dict[str, object] = field(default_factory=dict)
