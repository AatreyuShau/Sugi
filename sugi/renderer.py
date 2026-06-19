from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .vm import SugiVM


@dataclass(frozen=True)
class RenderNode:
    handle: int
    type: str
    properties: dict[str, Any]
    components: list[dict[str, Any]]
    children: tuple["RenderNode", ...] = field(default_factory=tuple)


class RenderTreeBuilder:
    """Backend-independent render tree generator for renderer adapters."""

    def build(self, vm: SugiVM) -> tuple[RenderNode, ...]:
        roots = [node for node in vm.heap.all() if node.parent is None]
        return tuple(self._build_node(vm, node.handle) for node in roots)

    def _build_node(self, vm: SugiVM, handle: int) -> RenderNode:
        node = vm.heap.get(handle)
        return RenderNode(
            handle=node.handle,
            type=node.type,
            properties=dict(node.properties),
            components=[{"type": component.type, **component.values} for component in node.components],
            children=tuple(self._build_node(vm, child) for child in node.children),
        )
