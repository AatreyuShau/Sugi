import json
from pathlib import Path

from examples.platformer.native.platformer_native import flatten, load_scene
from tools.export_render_tree import export_render_tree

SCENE = Path("examples/platformer/platformer.yaml")


def test_platformer_scene_drives_native_render_tree():
    vm, roots = load_scene()
    nodes = flatten(roots)
    player = next(node for node in nodes if "player" in str(node.properties.get("class", "")).split())
    assert vm.heap.get(player.handle).variables["grounded"] is False
    assert any(component["type"] == "PlatformerBody" for component in player.components)
    assert len([node for node in nodes if "solid" in str(node.properties.get("class", "")).split()]) == 3


def test_platformer_web_export_contains_goal_and_platforms(tmp_path):
    output = tmp_path / "render_tree.json"
    export_render_tree(SCENE, output)
    tree = json.loads(output.read_text(encoding="utf-8"))
    encoded = json.dumps(tree)
    assert "PlatformerBody" in encoded
    assert "Goal" in encoded
    assert "ledge_mid" in encoded
