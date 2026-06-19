from __future__ import annotations

import json
from typing import Any
try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised when PyYAML is unavailable
    yaml = None

from .bytecode import BytecodeProgram, Instruction, OpCode
from .assets import MaterialResource
from .scene import CompiledScene

_RESERVED = {"type", "id", "children", "variables", "styles", "events", "components", "on_click", "mounts", "animations", "states", "classes", "tags"}


class Compiler:
    def compile_yaml(self, source: str) -> BytecodeProgram:
        ast = yaml.safe_load(source) if yaml is not None else _simple_yaml_load(source)
        if not isinstance(ast, dict) or "page" not in ast:
            raise ValueError("SUGI YAML root must contain a page object")
        instructions: list[Instruction] = []
        self._emit_node(ast["page"], None, instructions, default_type="page")
        return BytecodeProgram(tuple(instructions))

    def compile_json(self, source: str) -> BytecodeProgram:
        ast = json.loads(source)
        return self.compile_mapping(ast)

    def compile_scene(self, source: str, source_format: str = "yaml") -> CompiledScene:
        ast = json.loads(source) if source_format == "json" else (yaml.safe_load(source) if yaml is not None else _simple_yaml_load(source))
        program = self.compile_mapping(ast)
        node_count = sum(1 for instruction in program.instructions if instruction.opcode == OpCode.CREATE_NODE)
        materials = self._parse_materials(ast.get("materials", {}) if isinstance(ast, dict) else {})
        return CompiledScene(program=program, node_count=node_count, source_format=source_format, materials=materials)

    def compile_mapping(self, ast: dict[str, Any]) -> BytecodeProgram:
        if not isinstance(ast, dict) or "page" not in ast:
            raise ValueError("SUGI scene root must contain a page object")
        instructions: list[Instruction] = []
        self._emit_node(ast["page"], None, instructions, default_type="page")
        return BytecodeProgram(tuple(instructions))

    def _parse_materials(self, specs: dict[str, Any]) -> dict[str, MaterialResource]:
        materials: dict[str, MaterialResource] = {}
        for name, spec in (specs or {}).items():
            if not isinstance(spec, dict) or not spec.get("vertex") or not spec.get("fragment"):
                raise ValueError(f"material {name!r} requires vertex and fragment shader paths")
            materials[name] = MaterialResource(name=name, vertex=spec["vertex"], fragment=spec["fragment"], uniforms=dict(spec.get("uniforms") or {}))
        return materials

    def _emit_node(self, spec: dict[str, Any], parent_id: str | None, out: list[Instruction], default_type: str | None = None) -> None:
        if not isinstance(spec, dict):
            raise ValueError("node definitions must be objects")
        node_type = spec.get("type", default_type)
        node_id = spec.get("id")
        if not node_type or not node_id:
            raise ValueError("each node requires an id and type")
        out.append(Instruction(OpCode.CREATE_NODE, {"id": node_id, "type": node_type}))
        if parent_id is not None:
            out.append(Instruction(OpCode.APPEND_CHILD, {"parent_id": parent_id, "child_id": node_id}))
        for key, value in spec.items():
            if key not in _RESERVED:
                out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": key, "value": value}))
        for key, value in (spec.get("variables") or {}).items():
            out.append(Instruction(OpCode.SET_VARIABLE, {"node_id": node_id, "variable": key, "value": value}))
        for key, value in (spec.get("styles") or {}).items():
            out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": f"style.{key}", "value": value}))
        if spec.get("animations"):
            out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": "animations", "value": spec["animations"]}))
        for state, value in (spec.get("states") or {}).items():
            out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": f"state.{state}", "value": value}))
        if spec.get("classes"):
            out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": "classes", "value": spec["classes"]}))
        if spec.get("tags"):
            out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": "tags", "value": spec["tags"]}))
        for component in spec.get("components") or []:
            out.append(Instruction(OpCode.SET_PROPERTY, {"node_id": node_id, "property": "component", "value": component}))
        events = dict(spec.get("events") or {})
        if "on_click" in spec:
            events["click"] = spec["on_click"]
        for event, handlers in events.items():
            out.append(Instruction(OpCode.REGISTER_EVENT, {"node_id": node_id, "event": event, "handlers": handlers}))
        for mount in spec.get("mounts") or []:
            out.append(Instruction(OpCode.MOUNT_PACKAGE, {"node_id": node_id, "package": mount}))
        for child in spec.get("children") or []:
            self._emit_node(child, node_id, out)



def _simple_yaml_load(source: str) -> dict[str, Any]:
    """Small dependency-free YAML subset loader for SUGI examples and tests."""
    lines = []
    for raw in source.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))
    index = 0

    def parse_scalar(text: str) -> Any:
        if text in {"true", "True"}:
            return True
        if text in {"false", "False"}:
            return False
        if text in {"null", "None"}:
            return None
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return text[1:-1]
        try:
            return int(text)
        except ValueError:
            return text

    def parse_block(indent: int) -> Any:
        nonlocal index
        if index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
            items = []
            while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
                text = lines[index][1][2:]
                index += 1
                if not text:
                    items.append(parse_block(indent + 2))
                elif ":" in text:
                    key, value = text.split(":", 1)
                    item: dict[str, Any] = {}
                    if value.strip():
                        item[key] = parse_scalar(value.strip())
                    elif index < len(lines) and lines[index][0] > indent:
                        item[key] = parse_block(lines[index][0])
                    else:
                        item[key] = None
                    while index < len(lines) and lines[index][0] > indent:
                        child_indent, child_text = lines[index]
                        if child_indent != indent + 2 or child_text.startswith("- "):
                            break
                        k, v = child_text.split(":", 1)
                        index += 1
                        item[k] = parse_scalar(v.strip()) if v.strip() else parse_block(lines[index][0])
                    items.append(item)
                else:
                    items.append(parse_scalar(text))
            return items
        mapping: dict[str, Any] = {}
        while index < len(lines) and lines[index][0] == indent:
            _, text = lines[index]
            key, value = text.split(":", 1)
            index += 1
            mapping[key] = parse_scalar(value.strip()) if value.strip() else parse_block(lines[index][0])
        return mapping

    return parse_block(0)
