from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Iterable

from .assets import AssetCache
from .dom import Node
from .vm import SugiVM

AUTO_UNIFORMS = {"iTime", "iResolution", "iMouse", "iFrame", "cameraPosition", "viewportSize"}


@dataclass
class RenderFrame:
    width: float
    height: float
    commands: list[dict[str, Any]] = field(default_factory=list)
    page_height: float | None = None


@dataclass(frozen=True)
class ShaderProgram:
    name: str
    vertex: str
    fragment: str
    uniforms: dict[str, Any]
    shadertoy: bool = False


class ShaderManager:
    """Compiles, validates, links, and caches user supplied shader programs."""

    def __init__(self, cache: AssetCache | None = None) -> None:
        self.cache = cache or AssetCache()
        self._programs: dict[str, ShaderProgram] = {}

    def compile(self, path: str) -> dict[str, Any]:
        return self.cache.load_shader(path).payload

    def link(self, name: str, vertex: str, fragment: str, uniforms: dict[str, Any] | None = None, shadertoy: bool = False) -> ShaderProgram:
        key = f"{name}:{vertex}:{fragment}:{shadertoy}"
        if key not in self._programs:
            self.compile(vertex)
            self.compile(fragment)
            program = ShaderProgram(name=name, vertex=vertex, fragment=fragment, uniforms=dict(uniforms or {}), shadertoy=shadertoy)
            self.validate(program)
            self._programs[key] = program
        return self._programs[key]

    def validate(self, program: ShaderProgram) -> None:
        if not program.vertex or not program.fragment:
            raise ValueError(f"shader program {program.name!r} requires vertex and fragment stages")

    def cache(self) -> dict[str, ShaderProgram]:  # pragma: no cover - compatibility alias
        return dict(self._programs)


class TextureManager:
    def __init__(self, cache: AssetCache | None = None) -> None:
        self.cache = cache or AssetCache()

    def load(self, source: str) -> dict[str, Any]:
        entry = self.cache.load_image(source)
        self.cache.textures.setdefault(source, entry)
        return entry.payload


@dataclass(frozen=True)
class RenderPass:
    name: str
    commands: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class RenderGraph:
    passes: tuple[RenderPass, ...]

    @property
    def commands(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for render_pass in self.passes:
            out.extend(render_pass.commands)
        return out


class SceneRenderer:
    """Retained renderer that traverses the VM DOM and owns all GPU draw commands."""

    def __init__(self, cache: AssetCache | None = None) -> None:
        self.started = time.monotonic()
        self.frame_index = 0
        self.cache = cache or AssetCache()
        self.shaders = ShaderManager(self.cache)
        self.textures = TextureManager(self.cache)
        self._last_graph: RenderGraph | None = None

    def render(self, vm: SugiVM) -> RenderFrame:
        graph = self.build_graph(vm)
        self._last_graph = graph
        root = self._root(vm)
        width = float(root.variables.get("viewport_width", root.properties.get("width", 800))) if root else 0
        height = float(root.variables.get("viewport_height", root.properties.get("height", 600))) if root else 0
        self.frame_index += 1
        return RenderFrame(width, height, graph.commands, float(root.properties.get("height", height)) if root else None)

    def present(self, vm: SugiVM) -> RenderFrame:
        return self.render(vm)

    def build_graph(self, vm: SugiVM) -> RenderGraph:
        root = self._root(vm)
        if root is None:
            return RenderGraph(())
        context = self._context(root)
        nodes = list(self._walk(root, vm))
        passes = (
            RenderPass("MaterialPass", tuple(self._material_commands(vm))),
            RenderPass("SpritePass", tuple(self._sprite_commands(nodes, context))),
            RenderPass("TextPass", tuple(self._text_commands(nodes))),
            RenderPass("ParticlePass", tuple(self._particle_commands(nodes))),
            RenderPass("VectorPass", tuple(self._vector_commands(nodes))),
            RenderPass("PostProcessPass", tuple(self._surface_commands(nodes, context))),
        )
        vm.heap.dirty_nodes.clear()
        for node in nodes:
            node.dirty = False
        return RenderGraph(passes)

    def _root(self, vm: SugiVM) -> Node | None:
        return next((node for node in vm.heap.all() if node.parent is None), None)

    def _walk(self, node: Node, vm: SugiVM) -> Iterable[Node]:
        yield node
        for child in node.children:
            yield from self._walk(vm.heap.get(child), vm)

    def _context(self, root: Node) -> dict[str, Any]:
        width = float(root.variables.get("viewport_width", root.properties.get("width", 800)))
        height = float(root.variables.get("viewport_height", root.properties.get("height", 600)))
        return {
            "iTime": time.monotonic() - self.started,
            "iResolution": [width, height, 1.0],
            "iMouse": [float(root.variables.get("mouse_x", 0)), float(root.variables.get("mouse_y", 0)), 0, 0],
            "iFrame": self.frame_index,
            "cameraPosition": self._camera(root),
            "viewportSize": [width, height],
        }

    def _camera(self, root: Node) -> list[float]:
        camera = root.properties.get("camera", {}) if isinstance(root.properties.get("camera"), dict) else {}
        return [float(camera.get("x", 0)), float(camera.get("y", root.variables.get("scroll_y", 0))), float(camera.get("zoom", 1.0))]

    def _material_commands(self, vm: SugiVM) -> Iterable[dict[str, Any]]:
        for name, material in vm.materials.items():
            shadertoy = bool(getattr(material, "shadertoy", False) or getattr(material, "uniforms", {}).get("shadertoy"))
            program = self.shaders.link(name, material.vertex, material.fragment, material.uniforms, shadertoy)
            self.cache.load_material(name, program.vertex, program.fragment, program.uniforms)
            yield {"kind": "CompileMaterial", "material": name, "vertex": program.vertex, "fragment": program.fragment, "shadertoy": program.shadertoy}

    def _sprite_commands(self, nodes: list[Node], context: dict[str, Any]) -> Iterable[dict[str, Any]]:
        batches: dict[tuple[str | None, str | None], list[Node]] = {}
        for node in nodes:
            if node.type not in {"sprite", "image"}:
                continue
            image = node.properties.get("image") or node.properties.get("source")
            material = node.properties.get("material")
            if image:
                self.textures.load(str(image))
            batches.setdefault((str(image) if image else None, str(material) if material else None), []).append(node)
        for (texture, material), batch_nodes in batches.items():
            if material:
                yield {"kind": "BindShader", "material": material}
                yield from self._auto_uniforms(context)
            if texture:
                yield {"kind": "BindTexture", "texture": texture}
            yield {"kind": "SpriteBatch", "texture": texture, "material": material, "count": len(batch_nodes)}
            for node in batch_nodes:
                p = node.properties
                if texture is None and material is None:
                    yield {"kind": "round_rect", "node": node.id, "x": float(p.get("x", 0)), "y": p.get("y", 0), "width": p.get("width", 0), "height": p.get("height", 0), "fill": p.get("color")}
                yield {"kind": "DrawQuad", "node": node.id, "x": p.get("x", 0), "y": p.get("y", 0), "width": p.get("width", 0), "height": p.get("height", 0)}

    def _vector_commands(self, nodes: list[Node]) -> Iterable[dict[str, Any]]:
        for node in nodes:
            if node.type != "pen":
                continue
            points = node.variables.get("points") or []
            if len(points) > 1:
                for a, b in zip(points, points[1:]):
                    yield {"kind": "line", "node": node.id, "x1": a.get("x", 0), "y1": a.get("y", 0), "x2": b.get("x", 0), "y2": b.get("y", 0)}
            else:
                yield {"kind": "polyline", "node": node.id, "points": points}

    def _surface_commands(self, nodes: list[Node], context: dict[str, Any]) -> Iterable[dict[str, Any]]:
        for node in nodes:
            if node.type not in {"surface", "shader_surface", "shader"}:
                continue
            material = node.properties.get("material") or node.properties.get("shader")
            if material:
                yield {"kind": "BindShader", "material": material}
                yield from self._auto_uniforms(context)
            p = node.properties
            yield {"kind": "shader_rect", "node": node.id, "material": material, "shader": node.properties.get("shader"), "x": p.get("x", 0), "y": p.get("y", 0), "width": p.get("width", 0), "height": p.get("height", 0), "strength": p.get("strength", 1)}
            yield {"kind": "DrawQuad", "node": node.id, "x": p.get("x", 0), "y": p.get("y", 0), "width": p.get("width", 0), "height": p.get("height", 0)}

    def _particle_commands(self, nodes: list[Node]) -> Iterable[dict[str, Any]]:
        for node in nodes:
            if node.type != "particle_system":
                continue
            p = node.properties
            yield {"kind": "particle", "node": node.id, "effect": p.get("effect", "custom"), "x": p.get("x", 0), "y": p.get("y", 0), "density": p.get("density", 0)}

    def _text_commands(self, nodes: list[Node]) -> Iterable[dict[str, Any]]:
        for node in nodes:
            if node.type != "text":
                continue
            p = node.properties
            yield {"kind": "wrapped_text", "node": node.id, "text": p.get("text", ""), "x": p.get("x", 0), "y": p.get("y", 0), "font": p.get("font", "default")}
            yield {"kind": "DrawText", "node": node.id, "text": p.get("text", ""), "x": p.get("x", 0), "y": p.get("y", 0), "font": p.get("font", "default")}

    def _auto_uniforms(self, context: dict[str, Any]) -> Iterable[dict[str, Any]]:
        for name in sorted(AUTO_UNIFORMS):
            yield {"kind": "SetUniform", "name": name, "value": context[name], "source": "auto"}
