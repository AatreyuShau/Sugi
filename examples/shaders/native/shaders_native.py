#!/usr/bin/env python3
from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path

SCENE = Path(__file__).resolve().parents[1] / "web" / "render_tree.json"


def draw_node(canvas: tk.Canvas, node: dict) -> None:
    p = node.get("properties", {})
    kind = node.get("type")
    if kind != "page":
        x, y, w, h = [float(p.get(k, 0)) for k in ("x", "y", "width", "height")]
        if w and h:
            canvas.create_rectangle(x, y, x + w, y + h, fill=p.get("color", "#1e293b"), outline=p.get("stroke", ""))
    if kind == "text" or p.get("text") or p.get("label"):
        canvas.create_text(float(p.get("x", 24)), float(p.get("y", 40)), anchor="w", fill=p.get("text_color", p.get("color", "#f8fafc")), text=p.get("text", p.get("label", node.get("id"))), font=("TkDefaultFont", int(p.get("font_size", 18)), "bold"))
    for child in node.get("children", []):
        draw_node(canvas, child)


def main() -> None:
    tree = json.loads(SCENE.read_text())
    root_props = tree[0].get("properties", {})
    app = tk.Tk()
    app.title("SUGI native showcase")
    canvas = tk.Canvas(app, width=int(root_props.get("width", 1280)), height=int(root_props.get("height", 720)), bg=root_props.get("background", "#020617"))
    canvas.pack(fill="both", expand=True)
    for node in tree:
        draw_node(canvas, node)
    app.mainloop()


if __name__ == "__main__":
    main()
