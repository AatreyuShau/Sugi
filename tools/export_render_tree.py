#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sugi.compiler import Compiler
from sugi.renderer import RenderNode, RenderTreeBuilder
from sugi.vm import SugiVM


def render_node_to_dict(node: RenderNode) -> dict[str, Any]:
    return {
        "handle": node.handle,
        "type": node.type,
        "id": node.id,
        "properties": node.properties,
        "components": node.components,
        "children": [render_node_to_dict(child) for child in node.children],
    }


def export_render_tree(source: Path, destination: Path) -> None:
    vm = SugiVM()
    vm.execute_scene(Compiler().compile_scene(source.read_text(encoding="utf-8")))
    roots = RenderTreeBuilder().build(vm)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps([render_node_to_dict(root) for root in roots], indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: export_render_tree.py <source.yaml> <destination.json>", file=sys.stderr)
        return 2
    export_render_tree(Path(argv[1]), Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
