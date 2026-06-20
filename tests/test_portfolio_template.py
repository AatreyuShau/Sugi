import json
from pathlib import Path

from sugi.compiler import Compiler
from sugi.vm import SugiVM
from tools.export_render_tree import export_render_tree

SCENE = Path("examples/shader_water/water.yaml")


def test_water_shader_export_contains_custom_material_metadata(tmp_path):
    vm = SugiVM()
    vm.execute_scene(Compiler().compile_scene(SCENE.read_text(encoding="utf-8")))
    assert vm.query("#water_surface")
    output = tmp_path / "water_render_tree.json"
    export_render_tree(SCENE, output)
    encoded = json.dumps(json.loads(output.read_text(encoding="utf-8")))
    assert "__materials" in encoded
    assert "shaders/screen.vert" in encoded
    assert "shaders/water.frag" in encoded
