from sugi.compiler import Compiler
from sugi.visual_renderer import SceneRenderer
from sugi.vm import SugiVM


def test_renderer_owns_visuals_after_application_mutates_scene_state():
    vm = SugiVM()
    vm.execute(Compiler().compile_yaml(
        """
page:
  id: app
  width: 320
  height: 240
  children:
    - type: sprite
      id: player
      x: 10
      y: 20
      width: 32
      height: 32
      color: "#00f"
    - type: particle_system
      id: rain
      x: 0
      y: 0
      width: 320
      height: 240
      effect: rain
      density: 50
    - type: shader_surface
      id: fog
      x: 0
      y: 0
      width: 320
      height: 240
      shader: fog
      strength: 0.2
"""
    ))
    player = vm.query("#player")[0]
    rain = vm.query("#rain")[0]
    fog = vm.query("#fog")[0]
    vm.set_property(player, "x", 100)
    vm.set_property(player, "color", "#ff0000")
    vm.set_property(rain, "density", 120)
    vm.set_property(fog, "strength", 1.0)
    frame = SceneRenderer().render(vm)
    assert any(command.get("kind") == "shader_rect" and command.get("strength") == 1.0 for command in frame.commands)
    assert any(command.get("kind") == "particle" and command.get("effect") == "rain" for command in frame.commands)
    assert any(command.get("kind") == "round_rect" and command.get("x") == 100.0 and command.get("fill") == "#ff0000" for command in frame.commands)
