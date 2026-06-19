import json
from pathlib import Path

from examples.portfolio_template.server.portfolio_server import PortfolioController
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


def test_portfolio_python_controller_owns_interaction_state_and_frame_commands():
    controller = PortfolioController()
    controller.handle_event({"type": "viewport", "width": 1440, "height": 900, "scrollY": 1300})
    controller.handle_event({"type": "mouse", "x": 720, "y": 360})
    page = controller.vm.heap.get(controller.page)
    assert page.variables["scroll_y"] == 1300
    assert page.variables["mouse_x"] == 720
    frame = controller.frame()
    kinds = {command["kind"] for command in frame["commands"]}
    assert "shader_rect" in kinds
    assert "wrapped_text" in kinds
    assert any(command.get("kind") in {"line", "polyline"} for command in frame["commands"])
