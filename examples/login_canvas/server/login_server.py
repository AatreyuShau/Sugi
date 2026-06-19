#!/usr/bin/env python3
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sugi.compiler import Compiler
from sugi.vm import SugiVM

SCENE = Path(__file__).resolve().parents[1] / "login.yaml"
WEB_DIR = Path(__file__).resolve().parents[1] / "web"
VALID_USERNAME = "demo"
VALID_PASSWORD = "sugi"


class LoginController:
    def __init__(self, scene: Path = SCENE) -> None:
        self.vm = SugiVM()
        self.vm.execute(Compiler().compile_yaml(scene.read_text(encoding="utf-8")))
        self.focused: int | None = None
        self.username = self.vm.query("#username")[0]
        self.password = self.vm.query("#password")[0]
        self.button = self.vm.query("#login_button")[0]
        self.status = self.vm.query("#status")[0]

    def handle_event(self, event: dict[str, Any]) -> None:
        if event.get("type") == "click":
            self._handle_click(float(event.get("x", -1)), float(event.get("y", -1)))
        if event.get("type") == "key":
            self._handle_key(str(event.get("key", "")))

    def frame(self) -> dict[str, Any]:
        root = self.vm.heap.get(self.vm.query("#login_scene")[0])
        return {"width": root.properties["width"], "height": root.properties["height"], "commands": self._draw_commands()}

    def _handle_click(self, x: float, y: float) -> None:
        hit = None
        for handle in (self.username, self.password, self.button):
            node = self.vm.heap.get(handle)
            if self._inside(node.properties, x, y):
                hit = handle
        if hit in (self.username, self.password):
            self._focus(hit)
            return
        self._focus(None)
        if hit == self.button:
            self._submit()

    def _handle_key(self, key: str) -> None:
        if key == "Tab":
            self._focus(self.password if self.focused == self.username else self.username)
            return
        if key == "Enter":
            self._submit()
            return
        if self.focused not in (self.username, self.password):
            return
        node = self.vm.heap.get(self.focused)
        current = str(node.properties.get("value", ""))
        if key == "Backspace":
            self.vm.set_property(self.focused, "value", current[:-1])
        elif len(key) == 1 and len(current) < 32:
            self.vm.set_property(self.focused, "value", current + key)

    def _submit(self) -> None:
        username = str(self.vm.heap.get(self.username).properties.get("value", ""))
        password = str(self.vm.heap.get(self.password).properties.get("value", ""))
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            self.vm.set_property(self.status, "text", "Welcome to SUGI!")
            self.vm.set_property(self.status, "color", "#22c55e")
        else:
            self.vm.set_property(self.status, "text", "Invalid credentials")
            self.vm.set_property(self.status, "color", "#fb7185")

    def _focus(self, handle: int | None) -> None:
        self.focused = handle
        for field in (self.username, self.password):
            self.vm.set_variable(field, "focused", field == handle)

    @staticmethod
    def _inside(properties: dict[str, Any], x: float, y: float) -> bool:
        return float(properties["x"]) <= x <= float(properties["x"]) + float(properties["width"]) and float(properties["y"]) <= y <= float(properties["y"]) + float(properties["height"])

    def _draw_commands(self) -> list[dict[str, Any]]:
        commands: list[dict[str, Any]] = []
        root = self.vm.heap.get(self.vm.query("#login_scene")[0])
        commands.append({"kind": "rect", "x": 0, "y": 0, "width": root.properties["width"], "height": root.properties["height"], "fill": root.properties["background"]})
        for handle in root.children:
            node = self.vm.heap.get(handle)
            p = node.properties
            if node.type == "panel":
                commands.append({"kind": "rect", "x": p["x"], "y": p["y"], "width": p["width"], "height": p["height"], "radius": p["radius"], "fill": p["color"]})
            if node.type == "text":
                commands.append({"kind": "text", "x": p["x"], "y": p["y"], "text": p["text"], "fill": p["color"], "size": 28 if node.id == "title" else 16, "weight": 700 if node.id == "title" else 400})
            if node.type == "input":
                focused = bool(node.variables.get("focused"))
                commands.append({"kind": "text", "x": p["x"], "y": p["y"] - 10, "text": p["label"], "fill": "#cbd5e1", "size": 14})
                commands.append({"kind": "rect", "x": p["x"], "y": p["y"], "width": p["width"], "height": p["height"], "radius": 10, "fill": "#0f172a", "stroke": "#38bdf8" if focused else "#334155", "lineWidth": 2})
                value = str(p.get("value", ""))
                if node.id == "password":
                    value = "•" * len(value)
                commands.append({"kind": "text", "x": p["x"] + 14, "y": p["y"] + 29, "text": value, "fill": "#f8fafc", "size": 18})
            if node.type == "button":
                commands.append({"kind": "rect", "x": p["x"], "y": p["y"], "width": p["width"], "height": p["height"], "radius": 12, "fill": p["color"]})
                commands.append({"kind": "text", "x": p["x"] + p["width"] / 2, "y": p["y"] + 31, "text": p["text"], "fill": "#082f49", "size": 18, "weight": 700, "align": "center"})
        return commands


controller = LoginController()


class LoginHandler(BaseHTTPRequestHandler):
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
    server = ThreadingHTTPServer(("127.0.0.1", 8765), LoginHandler)
    print("SUGI canvas login server: http://127.0.0.1:8765")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
