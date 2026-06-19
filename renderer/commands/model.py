from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class DrawCommand:
    kind: str
    payload: dict[str, Any]

    def to_json(self) -> dict[str, Any]:
        return {"kind": self.kind, **self.payload}
