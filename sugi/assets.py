from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp", "svg"}
SUPPORTED_SHADER_FORMATS = {"glsl", "wgsl"}
BUILT_IN_SHADERS = {
    "aurora", "water", "fog", "glass", "hologram", "liquid_glass",
    "chromatic_edge", "gradient_noise", "crt", "heat_distortion", "blur",
    "bloom", "vignette", "pixelate", "scanlines",
}


@dataclass
class CacheEntry:
    key: str
    payload: Any
    version: int = 0
    ready: bool = True


@dataclass
class AssetCache:
    """Backend-independent cache for images, shaders, textures, and fonts."""

    images: dict[str, CacheEntry] = field(default_factory=dict)
    shaders: dict[str, CacheEntry] = field(default_factory=dict)
    fonts: dict[str, CacheEntry] = field(default_factory=dict)
    textures: dict[str, CacheEntry] = field(default_factory=dict)

    def load_image(self, source: str) -> CacheEntry:
        ext = source.rsplit(".", 1)[-1].lower() if "." in source else ""
        if ext and ext not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"unsupported image format: {ext}")
        return self.images.setdefault(source, CacheEntry(source, {"source": source, "format": ext or "unknown"}))

    def load_shader(self, shader: str) -> CacheEntry:
        if shader in BUILT_IN_SHADERS:
            return self.shaders.setdefault(shader, CacheEntry(shader, {"name": shader, "builtin": True}))
        ext = shader.rsplit(".", 1)[-1].lower() if "." in shader else ""
        if ext not in SUPPORTED_SHADER_FORMATS:
            raise ValueError(f"custom shader must be GLSL or WGSL: {shader}")
        return self.shaders.setdefault(shader, CacheEntry(shader, {"source": shader, "builtin": False, "format": ext}))

    def invalidate(self, key: str) -> None:
        for bucket in (self.images, self.shaders, self.fonts, self.textures):
            if key in bucket:
                bucket[key].version += 1
                bucket[key].ready = False
