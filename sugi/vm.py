from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from .bytecode import BytecodeProgram, Instruction, OpCode
from .dom import Component, DomHeap, NodeHandle

Watcher = Callable[[dict[str, Any]], None]


class SugiVM:
    def __init__(self) -> None:
        self.heap = DomHeap()
        self._watchers: dict[NodeHandle, list[Watcher]] = defaultdict(list)
        self._mounted: dict[str, NodeHandle] = {}

    def execute(self, program: BytecodeProgram) -> None:
        for instruction in program.instructions:
            self.execute_instruction(instruction)

    def execute_instruction(self, instruction: Instruction) -> Any:
        p = instruction.payload
        match instruction.opcode:
            case OpCode.CREATE_NODE:
                return self.heap.create_node(p["type"], p.get("id"), p.get("metadata"))
            case OpCode.DELETE_NODE:
                return self.heap.delete(self._resolve(p))
            case OpCode.SET_PROPERTY:
                return self.set_property(self._resolve(p), p["property"], p.get("value"))
            case OpCode.SET_VARIABLE:
                return self.set_variable(self._resolve(p), p["variable"], p.get("value"))
            case OpCode.APPEND_CHILD:
                return self.heap.append_child(self._resolve(p, "parent"), self._resolve(p, "child"))
            case OpCode.REMOVE_CHILD:
                return self.heap.remove_child(self._resolve(p, "parent"), self._resolve(p, "child"))
            case OpCode.REGISTER_EVENT:
                return self.register_event(self._resolve(p), p["event"], p.get("handlers", []))
            case OpCode.MOUNT_PACKAGE:
                self._mounted[p["package"]] = self._resolve(p)
            case OpCode.UNMOUNT_PACKAGE:
                self._mounted.pop(p["package"], None)
            case OpCode.CALL:
                return {"call": p.get("name"), "args": p.get("args", [])}
            case OpCode.NOOP:
                return None

    def set_property(self, node: NodeHandle, name: str, value: Any) -> None:
        target = self.heap.get(node)
        if name == "component":
            if not isinstance(value, dict) or "type" not in value:
                raise ValueError("component property requires an object with a type")
            target.components.append(Component(value["type"], {k: v for k, v in value.items() if k != "type"}))
        else:
            target.properties[name] = value
        self._notify({"event": "property_changed", "node": node, "property": name, "value": value})

    def set_variable(self, node: NodeHandle, name: str, value: Any) -> None:
        self.heap.get(node).variables[name] = value
        self._notify({"event": "variable_changed", "node": node, "variable": name, "value": value})

    def register_event(self, node: NodeHandle, event: str, handlers: list[dict[str, Any]]) -> None:
        self.heap.get(node).events[event] = handlers

    def dispatch_event(self, node: NodeHandle, event: str, payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        path: list[NodeHandle] = []
        current: NodeHandle | None = node
        while current is not None:
            path.append(current)
            current = self.heap.get(current).parent
        deliveries = []
        for phase, handles in (("capture", reversed(path[1:])), ("target", [node]), ("bubble", path[1:])):
            for handle in handles:
                if event in self.heap.get(handle).events:
                    deliveries.append({"phase": phase, "node": handle, "event": event, "payload": payload or {}})
        return deliveries

    def watch(self, node: NodeHandle, callback: Watcher) -> None:
        self._watchers[node].append(callback)

    def query(self, selector: str) -> list[NodeHandle]:
        if selector.startswith("#"):
            found = self.heap.by_id(selector[1:])
            return [] if found is None else [found]
        if selector.startswith("[") and selector.endswith("]") and "=" in selector:
            key, value = selector[1:-1].split("=", 1)
            return [n.handle for n in self.heap.all() if n.properties.get(key) == value.strip('"\'')]
        parts = selector.split()
        nodes = self.heap.all()
        if len(parts) == 1:
            token = parts[0]
            if token.startswith("."):
                klass = token[1:]
                return [n.handle for n in nodes if klass in str(n.properties.get("class", "")).split()]
            return [n.handle for n in nodes if n.type == token]
        if len(parts) == 2:
            ancestors = set(self.query(parts[0]))
            return [n.handle for n in nodes if n.type == parts[1] and self._has_ancestor(n.handle, ancestors)]
        if len(parts) == 3 and parts[1] == ">":
            parents = set(self.query(parts[0]))
            return [n.handle for n in nodes if n.type == parts[2] and n.parent in parents]
        return []

    def _has_ancestor(self, node: NodeHandle, ancestors: set[NodeHandle]) -> bool:
        current = self.heap.get(node).parent
        while current is not None:
            if current in ancestors:
                return True
            current = self.heap.get(current).parent
        return False

    def _resolve(self, payload: dict[str, Any], prefix: str | None = None) -> NodeHandle:
        key = "node" if prefix is None else prefix
        if key in payload:
            return int(payload[key])
        id_key = "node_id" if prefix is None else f"{prefix}_id"
        found = self.heap.by_id(payload[id_key])
        if found is None:
            raise KeyError(f"unknown node id: {payload[id_key]}")
        return found

    def _notify(self, message: dict[str, Any]) -> None:
        for callback in self._watchers.get(message["node"], []):
            callback(message)
