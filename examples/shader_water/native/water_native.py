#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sugi.compiler import Compiler
from sugi.native_renderer import NativeCanvasRenderer
from sugi.renderer import RenderTreeBuilder
from sugi.vm import SugiVM

SCENE = Path(__file__).resolve().parents[1] / "water.yaml"


def load_scene() -> tuple[SugiVM, NativeCanvasRenderer, tk.Tk]:
    vm = SugiVM()
    vm.execute_scene(Compiler().compile_scene(SCENE.read_text(encoding="utf-8")))
    root = tk.Tk()
    root.title("SUGI Native Water Shader")
    canvas = tk.Canvas(root, width=800, height=450, bg="#020617", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    renderer = NativeCanvasRenderer(canvas, RenderTreeBuilder().build(vm), ROOT)
    return vm, renderer, root


def main() -> None:
    _vm, renderer, root = load_scene()

    def frame() -> None:
        renderer.render()
        root.after(16, frame)

    frame()
    root.mainloop()


if __name__ == "__main__":
    main()
