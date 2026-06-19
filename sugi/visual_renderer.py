from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

from .dom import Node
from .vm import SugiVM


@dataclass
class RenderFrame:
    width: float
    height: float
    commands: list[dict[str, Any]] = field(default_factory=list)
    page_height: float | None = None


class SceneRenderer:
    """Backend-neutral scene renderer that turns SUGI DOM nodes into frame commands.

    Applications mutate VM state only. This renderer owns traversal, visual effects,
    simple particles, shader surfaces, sprite/text/panel commands, and declarative
    animation interpolation data.
    """

    def __init__(self) -> None:
        self.started = time.monotonic()

    def render(self, vm: SugiVM) -> RenderFrame:
        roots = [node for node in vm.heap.all() if node.parent is None]
        if not roots:
            return RenderFrame(0, 0, [])
        root = roots[0]
        width = float(root.variables.get("viewport_width", root.properties.get("width", 800)))
        height = float(root.variables.get("viewport_height", root.properties.get("height", 600)))
        scale = width / max(float(root.properties.get("width", width)), 1)
        scroll = self._locked_scroll(vm, root, float(root.variables.get("scroll_y", 0)) / max(scale, 0.001))
        now = time.monotonic() - self.started
        commands: list[dict[str, Any]] = []
        background = root.properties.get("background")
        if background:
            commands.append({"kind": "rect", "x": 0, "y": 0, "width": width / scale, "height": height / scale, "fill": background})
        self._render_children(vm, root, commands, scroll, scale, height / scale, now)
        return RenderFrame(width, height, [{**command, "scale": scale} for command in commands], float(root.properties.get("height", height / scale)) * scale)

    def present(self, vm: SugiVM) -> RenderFrame:
        return self.render(vm)

    def _render_children(self, vm: SugiVM, parent: Node, commands: list[dict[str, Any]], scroll: float, scale: float, viewport_height: float, now: float) -> None:
        for handle in parent.children:
            node = vm.heap.get(handle)
            props = node.properties
            parallax = float(props.get("parallax", 0.35 if node.type in {"shader", "shader_surface"} else 0.82 if node.type in {"sprite", "image"} else 1.0))
            y = float(props.get("y", 0)) - scroll * parallax
            node_height = float(props.get("height", 80))
            if y > viewport_height + 300 or y + node_height < -320:
                continue
            if node.type in {"panel", "container", "section", "button", "canvas", "viewport"}:
                self._box(node, y, commands)
            elif node.type == "input":
                self._input(node, y, commands)
            elif node.type == "text":
                self._text(node, y, commands, viewport_height)
            elif node.type in {"sprite", "image"}:
                self._sprite(node, y, commands, vm, scale, now)
            elif node.type in {"shader", "shader_surface"}:
                self._shader_surface(node, y, commands, now)
            elif node.type == "particle_system":
                self._particles(node, y, commands, now)
            elif node.type == "pen":
                self._pen(node, y, commands, scale, now)
            self._render_children(vm, node, commands, scroll, scale, viewport_height, now)

    def _box(self, node: Node, y: float, commands: list[dict[str, Any]]) -> None:
        p = node.properties
        commands.append({"kind": "round_rect", "x": p.get("x", 0), "y": y, "width": p.get("width", 0), "height": p.get("height", 0), "radius": p.get("radius", 0), "fill": p.get("color", "rgba(15,23,42,.54)"), "stroke": p.get("stroke")})
        if node.type == "button" and p.get("text"):
            commands.append({"kind": "text", "x": float(p.get("x", 0)) + float(p.get("width", 0)) / 2, "y": y + float(p.get("height", 0)) * 0.64, "text": p["text"], "fill": p.get("text_color", "#082f49"), "size": p.get("font_size", 18), "weight": 700, "align": "center"})

    def _input(self, node: Node, y: float, commands: list[dict[str, Any]]) -> None:
        p = node.properties
        focused = bool(node.variables.get("focused"))
        commands.append({"kind": "text", "x": p.get("x", 0), "y": y - 10, "text": p.get("label", node.id), "fill": "#cbd5e1", "size": 14})
        commands.append({"kind": "round_rect", "x": p.get("x", 0), "y": y, "width": p.get("width", 0), "height": p.get("height", 0), "radius": 10, "fill": p.get("color", "#0f172a"), "stroke": "#38bdf8" if focused else "#334155", "lineWidth": 2})
        value = str(p.get("value", ""))
        if any(component.values.get("secret") for component in node.components if component.type == "TextInput"):
            value = "•" * len(value)
        commands.append({"kind": "text", "x": float(p.get("x", 0)) + 14, "y": y + 29, "text": value, "fill": "#f8fafc", "size": 18})

    def _text(self, node: Node, y: float, commands: list[dict[str, Any]], viewport_height: float) -> None:
        p = node.properties
        component = next((c for c in node.components if c.type == "Text"), None)
        values = component.values if component else {}
        alpha = 1 - min(1, abs(y - viewport_height * 0.45) / 460)
        commands.append({"kind": "wrapped_text", "x": p.get("x", 0), "y": y, "text": p.get("text", values.get("value", "")), "fill": p.get("color", "#fff"), "size": values.get("size", p.get("font_size", 20)), "weight": values.get("weight", p.get("weight", 500)), "maxWidth": values.get("max_width", p.get("max_width", 1050)), "alpha": max(0.15, alpha + 0.25)})

    def _sprite(self, node: Node, y: float, commands: list[dict[str, Any]], vm: SugiVM, scale: float, now: float) -> None:
        p = node.properties
        x, w, h = float(p.get("x", 0)), float(p.get("width", 0)), float(p.get("height", 0))
        root = next((n for n in vm.heap.all() if n.parent is None), None)
        mx = float(root.variables.get("mouse_x", -99999)) / max(scale, 0.001) if root else -99999
        my = float(root.variables.get("mouse_y", -99999)) / max(scale, 0.001) if root else -99999
        hover = math.hypot(mx - (x + w / 2), my - (y + h / 2)) < float(p.get("hover_radius", 260))
        lift = -float(p.get("hover_lift", 18)) if hover else 0
        command = {"kind": "shader_round_rect" if p.get("shader") else "round_rect", "shader": p.get("shader"), "x": x, "y": y + lift, "width": w, "height": h, "radius": p.get("radius", 28), "phase": now + x * 0.003, "fill": p.get("color", "#8b5cf6"), "stroke": "rgba(255,255,255,.75)" if hover else p.get("stroke", "rgba(255,255,255,.22)"), "lineWidth": 3 if hover else 1}
        commands.append(command)
        if p.get("label", node.id):
            commands.append({"kind": "text", "x": x + 28, "y": y + lift + h - 42, "text": str(p.get("label", node.id.replace("_", " "))), "fill": p.get("text_color", "rgba(255,255,255,.88)"), "size": p.get("font_size", 24), "weight": 700})

    def _shader_surface(self, node: Node, y: float, commands: list[dict[str, Any]], now: float) -> None:
        p = node.properties
        commands.append({"kind": "shader_rect", "shader": p.get("shader", "glow"), "x": p.get("x", 0), "y": y, "width": p.get("width", 0), "height": p.get("height", 0), "strength": p.get("strength", 1), "phase": now})
        if p.get("shader") in {"grid_warp", "crt"}:
            for x in range(int(p.get("x", 0)) + 20, int(float(p.get("x", 0)) + float(p.get("width", 0))), 54):
                commands.append({"kind": "line", "x1": x + math.sin(now + x * 0.01) * 18, "y1": y + 40, "x2": x + math.cos(now + x * 0.02) * 24, "y2": y + float(p.get("height", 0)) - 40, "stroke": "rgba(255,255,255,.12)", "width": 1})

    def _particles(self, node: Node, y: float, commands: list[dict[str, Any]], now: float) -> None:
        p = node.properties
        density = min(int(p.get("density", 120)), 1500)
        effect = p.get("effect", "dust")
        color = {"rain": "rgba(125,211,252,.45)", "snow": "rgba(255,255,255,.8)", "leaves": "rgba(132,204,22,.55)", "embers": "rgba(251,113,133,.7)", "sparks": "rgba(250,204,21,.8)", "dust": "rgba(203,213,225,.32)"}.get(effect, "rgba(255,255,255,.5)")
        width, height = float(p.get("width", 0)), float(p.get("height", 0))
        for i in range(0, density, max(1, density // 120)):
            x = float(p.get("x", 0)) + ((i * 47 + now * float(p.get("wind", 20))) % max(width, 1))
            yy = y + ((i * 83 + now * float(p.get("speed", 120))) % max(height, 1))
            commands.append({"kind": "particle", "effect": effect, "x": x, "y": yy, "size": p.get("size", 2), "color": color})

    def _pen(self, node: Node, y: float, commands: list[dict[str, Any]], scale: float, now: float) -> None:
        points = node.variables.get("points", [])
        if points:
            for index in range(1, len(points)):
                a, b = points[index - 1], points[index]
                alpha = index / max(len(points), 1) * 0.55
                commands.append({"kind": "line", "x1": a["x"] / scale, "y1": a["y"] / scale, "x2": b["x"] / scale, "y2": b["y"] / scale, "stroke": f"rgba(103,232,249,{alpha})", "width": 2 + index / max(len(points), 1) * 18, "cap": "round"})
        else:
            path = [{"x": x, "y": y + 260 + math.sin(x * 0.013 + now) * 46} for x in range(120, 1320, 30)]
            commands.append({"kind": "polyline", "points": path, "stroke": "rgba(244,114,182,.35)", "width": 18, "cap": "round"})

    def _locked_scroll(self, vm: SugiVM, root: Node, raw: float) -> float:
        locks = [vm.heap.get(child) for child in root.children if any(c.type == "ScrollLock" for c in vm.heap.get(child).components)]
        if not locks:
            return raw
        component = next(c for c in locks[0].components if c.type == "ScrollLock")
        start = float(component.values.get("start", root.variables.get("scroll_lock_start", 0)))
        end = float(component.values.get("end", root.variables.get("scroll_lock_end", start)))
        if raw < start:
            return raw
        if raw < end:
            return start + (raw - start) * 0.18
        return raw - (end - start) * 0.82
