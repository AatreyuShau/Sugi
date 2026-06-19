import json
from pathlib import Path

from sugi.compiler import Compiler
from sugi.vm import SugiVM
from tools.export_render_tree import export_render_tree


def test_tunnel_runner_scene_compiles_and_exports(tmp_path):
    scene = Path("examples/tunnel_runner_3d/scene.yaml")
    vm = SugiVM()
    vm.execute(Compiler().compile_yaml(scene.read_text(encoding="utf-8")))
    assert vm.query("#hovercraft")
    assert vm.query("#energy_ring")
    output = tmp_path / "tunnel_render_tree.json"
    export_render_tree(scene, output)
    encoded = json.dumps(json.loads(output.read_text(encoding="utf-8")))
    assert "Camera3D" in encoded
    assert "Ring3D" in encoded
