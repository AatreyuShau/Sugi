from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RenderTarget:
    name: str
    width: int
    height: int
    format: str = "rgba8"


@dataclass
class RenderTargetPool:
    """Shares offscreen render targets across shader sprites and post effects."""

    _available: dict[tuple[int, int, str], list[RenderTarget]] = field(default_factory=lambda: defaultdict(list))
    _leased: set[str] = field(default_factory=set)
    _counter: int = 0

    def acquire(self, width: int, height: int, format: str = "rgba8") -> RenderTarget:
        key = (int(width), int(height), format)
        if self._available[key]:
            target = self._available[key].pop()
        else:
            self._counter += 1
            target = RenderTarget(f"rt_{self._counter}", key[0], key[1], format)
        self._leased.add(target.name)
        return target

    def release(self, target: RenderTarget) -> None:
        if target.name in self._leased:
            self._leased.remove(target.name)
            self._available[(target.width, target.height, target.format)].append(target)


@dataclass
class UniformCache:
    values: dict[tuple[int, str], Any] = field(default_factory=dict)

    def update(self, node: int, uniform: str, value: Any) -> bool:
        key = (node, uniform)
        changed = self.values.get(key) != value
        self.values[key] = value
        return changed


@dataclass
class BatchKey:
    shader: str | None
    texture: str | None
    blend: str = "normal"
