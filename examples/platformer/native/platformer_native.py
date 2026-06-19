#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import tkinter as tk

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sugi.compiler import Compiler
from sugi.renderer import RenderNode, RenderTreeBuilder
from sugi.vm import SugiVM

SCENE = Path(__file__).resolve().parents[1] / "platformer.yaml"
WIDTH = 960
HEIGHT = 540


@dataclass
class Body:
    x: float
    y: float
    vx: float
    vy: float
    width: float
    height: float
    grounded: bool = False


def load_scene() -> tuple[SugiVM, tuple[RenderNode, ...]]:
    vm = SugiVM()
    vm.execute(Compiler().compile_yaml(SCENE.read_text(encoding="utf-8")))
    return vm, RenderTreeBuilder().build(vm)


def flatten(nodes: tuple[RenderNode, ...]) -> list[RenderNode]:
    result: list[RenderNode] = []
    for node in nodes:
        result.append(node)
        result.extend(flatten(node.children))
    return result


class PlatformerApp:
    def __init__(self) -> None:
        self.vm, self.roots = load_scene()
        self.nodes = flatten(self.roots)
        player = next(node for node in self.nodes if node.properties.get("class", "").find("player") >= 0)
        self.player_handle = player.handle
        self.player = Body(float(player.properties["x"]), float(player.properties["y"]), 0, 0, float(player.properties["width"]), float(player.properties["height"]))
        self.solid_nodes = [node for node in self.nodes if "solid" in str(node.properties.get("class", "")).split()]
        self.goal = next(node for node in self.nodes if node.properties.get("id") == "goal" or node.type == "sprite" and node.properties.get("color") == "#facc15")
        self.keys: set[str] = set()
        self.root = tk.Tk()
        self.root.title("SUGI Platformer Native")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#101827", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.bind("<KeyPress>", lambda event: self.keys.add(event.keysym.lower()))
        self.root.bind("<KeyRelease>", lambda event: self.keys.discard(event.keysym.lower()))

    def run(self) -> None:
        self.tick()
        self.root.mainloop()

    def tick(self) -> None:
        self.update_physics(1 / 60)
        self.draw()
        self.root.after(16, self.tick)

    def update_physics(self, dt: float) -> None:
        left = any(key in self.keys for key in {"a", "left"})
        right = any(key in self.keys for key in {"d", "right"})
        jump = any(key in self.keys for key in {"w", "space", "up"})
        speed = float(self.vm.heap.get(1).variables.get("move_speed", 260))
        gravity = float(self.vm.heap.get(1).variables.get("gravity", 1600))
        jump_velocity = float(self.vm.heap.get(1).variables.get("jump_velocity", -620))
        self.player.vx = (-speed if left else 0) + (speed if right else 0)
        if jump and self.player.grounded:
            self.player.vy = jump_velocity
            self.player.grounded = False
        self.player.vy += gravity * dt
        self.player.x += self.player.vx * dt
        self.player.y += self.player.vy * dt
        self.player.grounded = False
        for solid in self.solid_nodes:
            sx, sy, sw, sh = (float(solid.properties[name]) for name in ("x", "y", "width", "height"))
            if self.overlaps(self.player.x, self.player.y, self.player.width, self.player.height, sx, sy, sw, sh) and self.player.vy >= 0:
                self.player.y = sy - self.player.height
                self.player.vy = 0
                self.player.grounded = True
        self.player.x = max(0, min(WIDTH - self.player.width, self.player.x))
        if self.player.y > HEIGHT:
            self.player.x, self.player.y, self.player.vx, self.player.vy = 96, 368, 0, 0
        self.vm.set_property(self.player_handle, "x", round(self.player.x, 2))
        self.vm.set_property(self.player_handle, "y", round(self.player.y, 2))
        self.vm.set_variable(self.player_handle, "grounded", self.player.grounded)

    @staticmethod
    def overlaps(ax: float, ay: float, aw: float, ah: float, bx: float, by: float, bw: float, bh: float) -> bool:
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def draw(self) -> None:
        self.canvas.delete("all")
        for node in self.nodes:
            if node.type in {"sprite", "platform"}:
                source = self.vm.heap.get(node.handle).properties
                x, y, w, h = (float(source[name]) for name in ("x", "y", "width", "height"))
                self.canvas.create_rectangle(x, y, x + w, y + h, fill=str(source.get("color", "#ffffff")), outline="")
            if node.type == "text":
                self.canvas.create_text(float(node.properties["x"]), float(node.properties["y"]), anchor="nw", text=str(node.properties["text"]), fill=str(node.properties.get("color", "#ffffff")), font=("Arial", 16))
        gx, gy, gw, gh = (float(self.goal.properties[name]) for name in ("x", "y", "width", "height"))
        if self.overlaps(self.player.x, self.player.y, self.player.width, self.player.height, gx, gy, gw, gh):
            self.canvas.create_text(WIDTH / 2, 120, text="You reached the goal!", fill="#facc15", font=("Arial", 34, "bold"))


if __name__ == "__main__":
    PlatformerApp().run()
