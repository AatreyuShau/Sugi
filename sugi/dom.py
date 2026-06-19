from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

NodeHandle = int


@dataclass
class Component:
    type: str
    values: dict[str, Any] = field(default_factory=dict)


@dataclass
class Node:
    handle: NodeHandle
    id: str
    type: str
    parent: NodeHandle | None = None
    children: list[NodeHandle] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    components: list[Component] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    events: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


class DomHeap:
    def __init__(self) -> None:
        self._next: NodeHandle = 1
        self._nodes: dict[NodeHandle, Node] = {}
        self._ids: dict[str, NodeHandle] = {}

    def create_node(self, node_type: str, node_id: str | None = None, metadata: dict[str, Any] | None = None) -> NodeHandle:
        handle = self._next
        self._next += 1
        resolved_id = node_id or f"node_{handle}"
        if resolved_id in self._ids:
            raise ValueError(f"duplicate node id: {resolved_id}")
        self._nodes[handle] = Node(handle=handle, id=resolved_id, type=node_type, metadata=metadata or {})
        self._ids[resolved_id] = handle
        return handle

    def get(self, handle: NodeHandle) -> Node:
        try:
            return self._nodes[handle]
        except KeyError as exc:
            raise KeyError(f"unknown node handle: {handle}") from exc

    def by_id(self, node_id: str) -> NodeHandle | None:
        return self._ids.get(node_id)

    def delete(self, handle: NodeHandle) -> None:
        node = self.get(handle)
        for child in list(node.children):
            self.delete(child)
        if node.parent is not None and handle in self.get(node.parent).children:
            self.get(node.parent).children.remove(handle)
        self._ids.pop(node.id, None)
        del self._nodes[handle]

    def append_child(self, parent: NodeHandle, child: NodeHandle) -> None:
        parent_node = self.get(parent)
        child_node = self.get(child)
        if child_node.parent is not None and child in self.get(child_node.parent).children:
            self.get(child_node.parent).children.remove(child)
        child_node.parent = parent
        if child not in parent_node.children:
            parent_node.children.append(child)

    def remove_child(self, parent: NodeHandle, child: NodeHandle) -> None:
        parent_node = self.get(parent)
        if child in parent_node.children:
            parent_node.children.remove(child)
            self.get(child).parent = None

    def all(self) -> list[Node]:
        return list(self._nodes.values())
