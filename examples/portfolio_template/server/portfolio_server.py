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
from sugi.visual_renderer import SceneRenderer
from sugi.vm import SugiVM

SCENE = Path(__file__).resolve().parents[1] / "portfolio.yaml"
WEB_DIR = Path(__file__).resolve().parents[1] / "web"


class PortfolioController:
    """Application-side controller: mutates DOM state, never draws."""

    def __init__(self, scene: Path = SCENE) -> None:
        self.vm = SugiVM()
        self.vm.execute(Compiler().compile_yaml(scene.read_text(encoding="utf-8")))
        self.renderer = SceneRenderer()
        self.page = self.vm.query("#portfolio_page")[0]
        self.trails = self.vm.query("#mouse_trails")[0]
        self.vm.set_variable(self.page, "viewport_width", 1440)
        self.vm.set_variable(self.page, "viewport_height", 900)
        self.vm.set_variable(self.page, "scroll_y", 0)
        self.vm.set_variable(self.page, "mouse_x", 720)
        self.vm.set_variable(self.page, "mouse_y", 360)
        self.vm.set_variable(self.trails, "points", [])

    def handle_event(self, event: dict[str, Any]) -> None:
        if event.get("type") == "viewport":
            self.vm.set_variable(self.page, "viewport_width", float(event.get("width", 1440)))
            self.vm.set_variable(self.page, "viewport_height", float(event.get("height", 900)))
            self.vm.set_variable(self.page, "scroll_y", float(event.get("scrollY", 0)))
        if event.get("type") == "mouse":
            x = float(event.get("x", 720))
            y = float(event.get("y", 360))
            self.vm.set_variable(self.page, "mouse_x", x)
            self.vm.set_variable(self.page, "mouse_y", y)
            points = list(self.vm.heap.get(self.trails).variables.get("points", []))
            points.append({"x": x, "y": y})
            self.vm.set_variable(self.trails, "points", points[-42:])

    def frame(self) -> dict[str, Any]:
        frame = self.renderer.present(self.vm)
        return {"width": frame.width, "height": frame.height, "pageHeight": frame.page_height, "commands": frame.commands}


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
