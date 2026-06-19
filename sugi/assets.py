from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp", "svg"}
SUPPORTED_SHADER_FORMATS = {"vert", "frag", "glsl", "wgsl"}


@dataclass(frozen=True)
class MaterialResource:
    """Application-supplied shader material description."""

    name: str
    vertex: str
    fragment: str
    uniforms: dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    key: str
    payload: Any
    version: int = 0
    ready: bool = True


@dataclass
class AssetCache:
    """Backend-independent cache for images, shaders, textures, fonts, and materials."""

    images: dict[str, CacheEntry] = field(default_factory=dict)
    shaders: dict[str, CacheEntry] = field(default_factory=dict)
    fonts: dict[str, CacheEntry] = field(default_factory=dict)
    textures: dict[str, CacheEntry] = field(default_factory=dict)
    materials: dict[str, CacheEntry] = field(default_factory=dict)

    def load_image(self, source: str) -> CacheEntry:
        ext = source.rsplit(".", 1)[-1].lower() if "." in source else ""
        if ext and ext not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"unsupported image format: {ext}")
        return self.images.setdefault(source, CacheEntry(source, {"source": source, "format": ext or "unknown"}))

    def load_shader(self, shader: str) -> CacheEntry:
        ext = shader.rsplit(".", 1)[-1].lower() if "." in shader else ""
        if ext not in SUPPORTED_SHADER_FORMATS:
            raise ValueError(f"shader must be an application-supplied GLSL/WGSL stage: {shader}")
        stage = "vertex" if ext in {"vert"} else "fragment" if ext in {"frag"} else "source"
        return self.shaders.setdefault(shader, CacheEntry(shader, {"source": shader, "stage": stage, "format": ext}))

    def load_material(self, name: str, vertex: str, fragment: str, uniforms: dict[str, Any] | None = None) -> CacheEntry:
        self.load_shader(vertex)
        self.load_shader(fragment)
        material = MaterialResource(name=name, vertex=vertex, fragment=fragment, uniforms=dict(uniforms or {}))
        return self.materials.setdefault(name, CacheEntry(name, material))

    def invalidate(self, key: str) -> None:
        for bucket in (self.images, self.shaders, self.fonts, self.textures, self.materials):
            if key in bucket:
                bucket[key].version += 1
                bucket[key].ready = False
