from __future__ import annotations

import math
import time
import tkinter as tk
from pathlib import Path
from typing import Any

from .renderer import RenderNode


class NativeCanvasRenderer:
    """Tkinter debug renderer for native examples.

    This backend consumes the same VM render tree as the web renderer. It does not
    ask applications to draw shader rectangles or image sprites directly; apps
    mutate VM state and hand the exported/current render tree to this renderer.
    """

    def __init__(self, canvas: tk.Canvas, roots: tuple[RenderNode, ...], base_path: Path | None = None) -> None:
        self.canvas = canvas
        self.roots = roots
        self.base_path = base_path or Path.cwd()
        self.started = time.monotonic()
        self._images: dict[str, tk.PhotoImage] = {}
        self.materials = self._materials()

    def render(self, camera_x: float = 0.0) -> None:
        now = time.monotonic() - self.started
        self.canvas.delete("all")
        for node in self._flatten(self.roots):
            self._draw_node(node, now, camera_x)

    def _materials(self) -> dict[str, dict[str, Any]]:
        root = next((node for node in self._flatten(self.roots) if node.type == "page"), None)
        return dict(root.properties.get("__materials", {})) if root else {}

    def _flatten(self, nodes: tuple[RenderNode, ...]) -> list[RenderNode]:
        out: list[RenderNode] = []
        for node in nodes:
            out.append(node)
            out.extend(self._flatten(node.children))
        return out

    def _draw_node(self, node: RenderNode, now: float, camera_x: float) -> None:
        p = node.properties
        if node.type in {"shader_surface", "surface"} and p.get("material"):
            self._draw_material_surface(node, now, camera_x)
        elif node.type in {"sprite", "image"}:
            self._draw_sprite(node, now, camera_x)
        elif node.type == "platform":
            self._draw_rect(node, camera_x)
        elif node.type == "text":
            self.canvas.create_text(float(p.get("x", 0)), float(p.get("y", 0)), anchor="nw", text=str(p.get("text", "")), fill=str(p.get("color", "#ffffff")), font=("Arial", int(p.get("font_size", 16)), "bold"))

    def _draw_material_surface(self, node: RenderNode, now: float, camera_x: float) -> None:
        p = node.properties
        material = self.materials.get(str(p.get("material")), {})
        fragment = str(material.get("fragment", ""))
        x = float(p.get("x", 0)) - camera_x * float(p.get("parallax", 1))
        y = float(p.get("y", 0))
        w = float(p.get("width", 0))
        h = float(p.get("height", 0))
        if "water" in fragment or p.get("material") == "water":
            self._draw_water_material(x, y, w, h, now)
            return
        steps = 24
        for i in range(steps):
            t = i / max(steps - 1, 1)
            r = int(6 + 80 * t)
            g = int(30 + 120 * (0.5 + 0.5 * math.sin(now + t * math.pi)))
            b = int(80 + 130 * (1 - t))
            self.canvas.create_rectangle(x, y + h * t, x + w, y + h * (t + 1 / steps), fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    def _draw_water_material(self, x: float, y: float, w: float, h: float, now: float) -> None:
        self.canvas.create_rectangle(x, y, x + w, y + h, fill="#05364f", outline="")
        for pass_index, color_width in enumerate((("#67e8f9", 4), ("#38bdf8", 9), ("#0ea5e9", 16))):
            color, width = color_width
            points: list[float] = []
            for px in range(0, max(1, int(w)) + 1, 14):
                wave = math.sin((px * 0.055) + now * (1.4 + pass_index * 0.3)) * (8 + pass_index * 3)
                points.extend([x + px, y + h * 0.42 + wave])
            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=width, smooth=True)
        self.canvas.create_rectangle(x, y + h * 0.45, x + w, y + h, fill="#075985", outline="")

    def _draw_sprite(self, node: RenderNode, now: float, camera_x: float) -> None:
        p = node.properties
        if p.get("material"):
            self._draw_material_surface(node, now, camera_x)
            if not (p.get("image") or p.get("source")):
                return
        source = p.get("image") or p.get("source")
        x = float(p.get("x", 0)) - camera_x
        y = float(p.get("y", 0))
        w = float(p.get("width", 0))
        h = float(p.get("height", 0))
        if source and str(source).lower().endswith((".png", ".gif")):
            image = self._load_photo(str(source))
            if image:
                self.canvas.create_image(x, y, anchor="nw", image=image)
                return
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=str(p.get("color", "#ffffff")), outline="")

    def _draw_rect(self, node: RenderNode, camera_x: float) -> None:
        p = node.properties
        x = float(p.get("x", 0)) - camera_x
        y, w, h = (float(p.get(name, 0)) for name in ("y", "width", "height"))
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=str(p.get("color", "#334155")), outline="")

    def _load_photo(self, source: str) -> tk.PhotoImage | None:
        if source in self._images:
            return self._images[source]
        path = (self.base_path / source).resolve()
        if not path.exists():
            return None
        try:
            self._images[source] = tk.PhotoImage(file=str(path))
        except tk.TclError:
            return None
        return self._images[source]
