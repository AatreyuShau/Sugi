#!/usr/bin/env python3
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sugi.compiler import Compiler
from sugi.vm import SugiVM

SCENE = Path(__file__).resolve().parents[1] / "portfolio.yaml"
WEB_DIR = Path(__file__).resolve().parents[1] / "web"


class PortfolioController:
    def __init__(self, scene: Path = SCENE) -> None:
        self.vm = SugiVM()
        self.vm.execute(Compiler().compile_yaml(scene.read_text(encoding="utf-8")))
        self.page = self.vm.query("#portfolio_page")[0]
        self.mouse_points: list[dict[str, float]] = []
        self.started = time.monotonic()
        page = self.vm.heap.get(self.page)
        page.variables.update({"viewport_width": 1440, "viewport_height": 900, "scroll_y": 0, "mouse_x": 720, "mouse_y": 360})

    def handle_event(self, event: dict[str, Any]) -> None:
        page = self.vm.heap.get(self.page)
        if event.get("type") == "viewport":
            self.vm.set_variable(self.page, "viewport_width", float(event.get("width", page.variables["viewport_width"])))
            self.vm.set_variable(self.page, "viewport_height", float(event.get("height", page.variables["viewport_height"])))
            self.vm.set_variable(self.page, "scroll_y", float(event.get("scrollY", page.variables["scroll_y"])))
        if event.get("type") == "mouse":
            x = float(event.get("x", page.variables["mouse_x"]))
            y = float(event.get("y", page.variables["mouse_y"]))
            self.vm.set_variable(self.page, "mouse_x", x)
            self.vm.set_variable(self.page, "mouse_y", y)
            self.mouse_points.append({"x": x, "y": y})
            self.mouse_points = self.mouse_points[-42:]

    def frame(self) -> dict[str, Any]:
        page = self.vm.heap.get(self.page)
        width = float(page.variables["viewport_width"])
        height = float(page.variables["viewport_height"])
        scale = width / float(page.properties["width"])
        scroll = self._locked_scroll(float(page.variables["scroll_y"]) / max(scale, 0.001))
        now = time.monotonic() - self.started
        commands = self._commands(width, height, scale, scroll, now)
        return {"width": width, "height": height, "pageHeight": float(page.properties["height"]) * scale, "commands": commands}

    @staticmethod
    def _locked_scroll(raw: float) -> float:
        start, end = 1180, 1980
        if raw < start:
            return raw
        if raw < end:
            return start + (raw - start) * 0.18
        return raw - (end - start) * 0.82

    def _commands(self, width: float, height: float, scale: float, scroll: float, now: float) -> list[dict[str, Any]]:
        commands: list[dict[str, Any]] = [{"kind": "rect", "x": 0, "y": 0, "width": width, "height": height, "fill": "#050816"}]
        page = self.vm.heap.get(self.page)
        mouse_x = float(page.variables["mouse_x"]) / max(scale, 0.001)
        mouse_y = float(page.variables["mouse_y"]) / max(scale, 0.001)
        for child in page.children:
            node = self.vm.heap.get(child)
            props = node.properties
            parallax = 0.35 if node.type == "shader" else 0.82 if node.type == "sprite" else 1.0
            y = float(props.get("y", 0)) - scroll * parallax
            node_height = float(props.get("height", 80))
            if y > height / scale + 260 or y + node_height < -280:
                continue
            if node.type == "shader":
                commands.extend(self._shader_commands(node.id, props, y, now))
            elif node.type == "section":
                commands.append({"kind": "round_rect", "x": props["x"], "y": y, "width": props["width"], "height": props["height"], "radius": 36, "fill": "rgba(15,23,42,.54)", "stroke": "rgba(255,255,255,.16)"})
            elif node.type == "sprite":
                commands.extend(self._sprite_commands(node.id, props, y, mouse_x, mouse_y, now))
            elif node.type == "pen":
                commands.extend(self._pen_commands(node.id, y, now, scale))
            elif node.type == "text":
                progress = 1 - min(1, abs(y - (height / scale) * 0.45) / 460)
                commands.extend(self._text_commands(node, y, max(0.15, progress + 0.25)))
        commands.append({"kind": "text", "x": 24, "y": height / scale - 24, "text": f"Python-rendered frame · scroll {round(scroll)} · DOM nodes {len(page.children) + 1}", "fill": "rgba(255,255,255,.7)", "size": 14})
        return [{**command, "scale": scale} for command in commands]

    def _shader_commands(self, node_id: str, props: dict[str, Any], y: float, now: float) -> list[dict[str, Any]]:
        shader = str(props.get("shader", "aurora"))
        commands = [{"kind": "shader_rect", "shader": shader, "x": props["x"], "y": y, "width": props["width"], "height": props["height"], "phase": now}]
        if node_id == "lock_shader":
            for x in range(100, 1340, 54):
                commands.append({"kind": "line", "x1": x + math.sin(now + x * 0.01) * 18, "y1": y + 40, "x2": x + math.cos(now + x * 0.02) * 24, "y2": y + 720, "stroke": "rgba(255,255,255,.12)", "width": 1})
        return commands

    def _sprite_commands(self, node_id: str, props: dict[str, Any], y: float, mouse_x: float, mouse_y: float, now: float) -> list[dict[str, Any]]:
        x = float(props["x"])
        w = float(props["width"])
        h = float(props["height"])
        hover = math.hypot(mouse_x - (x + w / 2), mouse_y - (y + h / 2)) < 260
        lift = -18 if hover else 0
        return [
            {"kind": "shader_round_rect", "shader": props.get("shader", "gradient_noise"), "x": x, "y": y + lift, "width": w, "height": h, "radius": 28, "phase": now + x * 0.003, "stroke": "rgba(255,255,255,.75)" if hover else "rgba(255,255,255,.22)", "lineWidth": 3 if hover else 1},
            {"kind": "text", "x": x + 28, "y": y + lift + h - 42, "text": node_id.replace("_", " "), "fill": "rgba(255,255,255,.88)", "size": 24, "weight": 700},
        ]

    def _pen_commands(self, node_id: str, y: float, now: float, scale: float) -> list[dict[str, Any]]:
        if node_id == "mouse_trails":
            commands = []
            for index in range(1, len(self.mouse_points)):
                a = self.mouse_points[index - 1]
                b = self.mouse_points[index]
                alpha = index / max(len(self.mouse_points), 1) * 0.55
                commands.append({"kind": "line", "x1": a["x"] / scale, "y1": a["y"] / scale, "x2": b["x"] / scale, "y2": b["y"] / scale, "stroke": f"rgba(103,232,249,{alpha})", "width": 2 + index / max(len(self.mouse_points), 1) * 18, "cap": "round"})
            return commands
        points = []
        for x in range(120, 1320, 30):
            points.append({"x": x, "y": y + 260 + math.sin(x * 0.013 + now) * 46})
        return [{"kind": "polyline", "points": points, "stroke": "rgba(244,114,182,.35)", "width": 18, "cap": "round"}]

    def _text_commands(self, node: Any, y: float, alpha: float) -> list[dict[str, Any]]:
        props = node.properties
        text_component = next((component for component in node.components if component.type == "Text"), None)
        values = text_component.values if text_component else {}
        return [{"kind": "wrapped_text", "x": props["x"], "y": y, "text": props["text"], "fill": props.get("color", "#fff"), "size": values.get("size", 20), "weight": values.get("weight", 500), "maxWidth": values.get("max_width", 1050), "alpha": alpha}]


controller = PortfolioController()


class PortfolioHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/frame":
            self._json(controller.frame())
            return
        target = WEB_DIR / ("index.html" if self.path in {"/", "/index.html"} else self.path.lstrip("/"))
        if target.resolve().is_relative_to(WEB_DIR.resolve()) and target.exists():
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(target.read_bytes())
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/event":
            self.send_error(404)
            return
        length = int(self.headers.get("content-length", "0"))
        controller.handle_event(json.loads(self.rfile.read(length) or b"{}"))
        self._json({"success": True})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _json(self, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8766), PortfolioHandler)
    print("SUGI Python portfolio server: http://127.0.0.1:8766")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
