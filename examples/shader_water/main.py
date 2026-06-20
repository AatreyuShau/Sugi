from pathlib import Path
from sugi.compiler import Compiler
from sugi.vm import SugiVM
from sugi.visual_renderer import SceneRenderer

scene = Path(__file__).with_name("water.yaml").read_text()
vm = SugiVM()
vm.execute_scene(Compiler().compile_scene(scene))
frame = SceneRenderer().render(vm)
print(frame.commands)
