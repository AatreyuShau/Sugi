from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .assets import MaterialResource


@dataclass(frozen=True)
class AstNode:
    """Language-neutral SUGI node produced by source parsers."""

    type: str
    id: str
    properties: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    components: tuple[dict[str, Any], ...] = ()
    animations: dict[str, Any] = field(default_factory=dict)
    events: dict[str, Any] = field(default_factory=dict)
    children: tuple["AstNode", ...] = ()


@dataclass(frozen=True)
class SceneAst:
    """Parsed scene before validation and compilation."""

    root: AstNode
    source_format: str = "yaml"


@dataclass(frozen=True)
class CompiledScene:
    """Runtime-ready scene artifact; runtime never reparses source files."""

    program: Any
    node_count: int
    source_format: str
    diagnostics: tuple[str, ...] = ()
    materials: dict[str, MaterialResource] = field(default_factory=dict)

    def encode(self) -> bytes:
        return self.program.encode()
