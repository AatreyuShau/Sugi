import json
from pathlib import Path

from sugi.compiler import Compiler
from sugi.vm import SugiVM
from tools.export_render_tree import export_render_tree

SCENE = Path("examples/portfolio_template/portfolio.yaml")


def test_portfolio_template_exports_shader_sprite_and_pen_capabilities(tmp_path):
    vm = SugiVM()
    vm.execute(Compiler().compile_yaml(SCENE.read_text(encoding="utf-8")))
    assert vm.query("#scroll_lock_story")
    assert vm.query("#mouse_trails")
    output = tmp_path / "portfolio_render_tree.json"
    export_render_tree(SCENE, output)
    encoded = json.dumps(json.loads(output.read_text(encoding="utf-8")))
    assert "FullFrameShader" in encoded
    assert "PenLayer" in encoded
    assert "ImageSprite" in encoded
    assert "ShaderSprite" in encoded
