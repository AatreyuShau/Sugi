import json
from pathlib import Path

from sugi.compiler import Compiler
from sugi.vm import SugiVM
from tools.export_render_tree import export_render_tree


def test_water_shader_scene_compiles_and_exports_materials(tmp_path):
    scene = Path("examples/shader_water/water.yaml")
    vm = SugiVM()
    vm.execute_scene(Compiler().compile_scene(scene.read_text(encoding="utf-8")))
    assert vm.query("#water_surface")
    assert "water" in vm.materials
    output = tmp_path / "water_render_tree.json"
    export_render_tree(scene, output)
    tree = json.loads(output.read_text(encoding="utf-8"))
    assert tree[0]["properties"]["__materials"]["water"]["fragment"] == "shaders/water.frag"
