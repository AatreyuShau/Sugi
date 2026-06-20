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
from sugi.native_renderer import NativeCanvasRenderer
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


def node_classes(node: RenderNode) -> set[str]:
    return set(str(node.properties.get("class", "")).split())


class PlatformerApp:
    def __init__(self) -> None:
        self.vm, self.roots = load_scene()
        self.nodes = flatten(self.roots)
        self.root_node = next(node for node in self.nodes if node.type == "page")
        player = next(node for node in self.nodes if "player" in node_classes(node))
        self.player_handle = player.handle
        self.player = Body(float(player.properties["x"]), float(player.properties["y"]), 0, 0, float(player.properties["width"]), float(player.properties["height"]))
        self.solid_nodes = [node for node in self.nodes if "solid" in node_classes(node)]
        self.goal = next(node for node in self.nodes if "goal" in node_classes(node))
        self.keys: set[str] = set()
        self.camera_x = 0.0
        self.tick_count = 0
        self.app = tk.Tk()
        self.app.title("SUGI Horizontal Platformer Native")
        self.canvas = tk.Canvas(self.app, width=WIDTH, height=HEIGHT, bg="#06111f", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = NativeCanvasRenderer(self.canvas, self.roots, ROOT)
        self.app.bind("<KeyPress>", lambda event: self.keys.add(event.keysym.lower()))
        self.app.bind("<KeyRelease>", lambda event: self.keys.discard(event.keysym.lower()))

    def run(self) -> None:
        self.tick()
        self.app.mainloop()

    def tick(self) -> None:
        self.update_physics(1 / 60)
        self.draw()
        self.tick_count += 1
        self.app.after(16, self.tick)

    def update_physics(self, dt: float) -> None:
        left = any(key in self.keys for key in {"a", "left"})
        right = any(key in self.keys for key in {"d", "right"})
        jump = any(key in self.keys for key in {"w", "space", "up"})
        root = self.vm.heap.get(self.root_node.handle)
        speed = float(root.variables.get("move_speed", 340))
        gravity = float(root.variables.get("gravity", 1600))
        jump_velocity = float(root.variables.get("jump_velocity", -650))
        world_width = float(root.properties.get("world_width", WIDTH))
        self.player.vx = (-speed if left else 0) + (speed if right else 0)
        if jump and self.player.grounded:
            self.player.vy = jump_velocity
            self.player.grounded = False
        self.player.vy += gravity * dt
        previous_y = self.player.y
        self.player.x += self.player.vx * dt
        self.player.y += self.player.vy * dt
        self.player.grounded = False
        for solid in self.solid_nodes:
            sx, sy, sw, sh = (float(solid.properties[name]) for name in ("x", "y", "width", "height"))
            falling_onto = previous_y + self.player.height <= sy + 8 and self.player.vy >= 0
            if falling_onto and self.overlaps(self.player.x, self.player.y, self.player.width, self.player.height, sx, sy, sw, sh):
                self.player.y = sy - self.player.height
                self.player.vy = 0
                self.player.grounded = True
        self.player.x = max(0, min(world_width - self.player.width, self.player.x))
        if self.player.y > HEIGHT + 180:
            self.player.x, self.player.y, self.player.vx, self.player.vy = 96, 364, 0, 0
        target_camera = max(0, min(world_width - WIDTH, self.player.x - WIDTH * 0.42))
        self.camera_x += (target_camera - self.camera_x) * 0.12
        self.vm.set_property(self.player_handle, "x", round(self.player.x, 2))
        self.vm.set_property(self.player_handle, "y", round(self.player.y, 2))
        self.vm.set_variable(self.player_handle, "grounded", self.player.grounded)

    @staticmethod
    def overlaps(ax: float, ay: float, aw: float, ah: float, bx: float, by: float, bw: float, bh: float) -> bool:
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def draw(self) -> None:
        self.roots = RenderTreeBuilder().build(self.vm)
        self.renderer.roots = self.roots
        self.renderer.materials = self.renderer._materials()
        self.renderer.render(self.camera_x)
        gx, gy, gw, gh = (float(self.goal.properties[name]) for name in ("x", "y", "width", "height"))
        if self.overlaps(self.player.x, self.player.y, self.player.width, self.player.height, gx, gy, gw, gh):
            self.canvas.create_text(WIDTH / 2, 120, text="You reached the hologram gate!", fill="#facc15", font=("Arial", 34, "bold"))


if __name__ == "__main__":
    PlatformerApp().run()
