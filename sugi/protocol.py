from __future__ import annotations

from typing import Any

from .vm import SugiVM


class ProtocolServer:
    """Transport-independent JSON-RPC style command dispatcher."""

    def __init__(self, vm: SugiVM) -> None:
        self.vm = vm

    def handle(self, message: dict[str, Any]) -> dict[str, Any]:
        try:
            result = self._dispatch(message)
            response = {"success": True}
            if "id" in message:
                response["id"] = message["id"]
            if result is not None:
                response["result"] = result
            return response
        except Exception as exc:  # command boundary converts failures to protocol errors
            return {"success": False, "id": message.get("id"), "error": str(exc)}

    def _dispatch(self, message: dict[str, Any]) -> Any:
        command = message["command"]
        if command == "create_node":
            return self.vm.heap.create_node(message["type"], message.get("node_id"))
        if command == "delete_node":
            return self.vm.heap.delete(message["node"])
        if command == "get_node":
            node = self.vm.heap.get(message["node"])
            return {
                "handle": node.handle,
                "id": node.id,
                "type": node.type,
                "parent": node.parent,
                "children": node.children,
                "properties": node.properties,
                "variables": node.variables,
                "components": [{"type": c.type, **c.values} for c in node.components],
                "metadata": node.metadata,
            }
        if command == "set_property":
            return self.vm.set_property(message["node"], message["property"], message.get("value"))
        if command == "set_variable":
            return self.vm.set_variable(message["node"], message["variable"], message.get("value"))
        if command == "append_child":
            return self.vm.heap.append_child(message["parent"], message["child"])
        if command == "remove_child":
            return self.vm.heap.remove_child(message["parent"], message["child"])
        if command == "query":
            return self.vm.query(message["selector"])
        if command == "dispatch_event":
            return self.vm.dispatch_event(message["node"], message["event"], message.get("payload"))
        if command == "play_animation":
            return self.vm.play_animation(message["node"], message["animation"])
        if command in {"mount", "unmount", "subscribe", "unsubscribe", "call", "watch"}:
            return {"accepted": True, "command": command}
        raise ValueError(f"unsupported command: {command}")
