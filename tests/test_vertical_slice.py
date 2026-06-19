from sugi.bytecode import BytecodeProgram, MAGIC, OpCode
from sugi.compiler import Compiler
from sugi.protocol import ProtocolServer
from sugi.renderer import RenderTreeBuilder
from sugi.vm import SugiVM

SOURCE = """
page:
  id: main
  children:
    - type: panel
      id: inventory
      class: inventory
      variables:
        open: true
      styles:
        layout: stack
      children:
        - type: button
          id: save_button
          text: Save
          on_click:
            - call: save_game
          components:
            - type: Text
              value: Save
            - type: Button
"""


def test_compiler_emits_binary_bytecode_round_trip():
    program = Compiler().compile_yaml(SOURCE)
    encoded = program.encode()
    assert encoded.startswith(MAGIC)
    decoded = BytecodeProgram.decode(encoded)
    assert decoded.instructions[0].opcode == OpCode.CREATE_NODE
    assert any(i.opcode == OpCode.REGISTER_EVENT for i in decoded.instructions)


def test_vm_dom_queries_events_watchers_and_render_tree():
    vm = SugiVM()
    vm.execute(Compiler().compile_yaml(SOURCE))
    save = vm.query("#save_button")[0]
    inventory = vm.query(".inventory")[0]
    assert save in vm.query("panel button")
    assert save in vm.query("panel > button")
    assert vm.heap.get(save).properties["text"] == "Save"
    assert vm.heap.get(inventory).variables["open"] is True
    seen = []
    vm.watch(save, seen.append)
    vm.set_property(save, "data-rarity", "legendary")
    assert vm.query("[data-rarity=legendary]") == [save]
    assert seen[-1]["event"] == "property_changed"
    deliveries = vm.dispatch_event(save, "click")
    assert deliveries[-1]["phase"] == "target"
    render_roots = RenderTreeBuilder().build(vm)
    assert render_roots[0].children[0].children[0].components[0]["type"] == "Text"


def test_protocol_is_transport_independent():
    vm = SugiVM()
    server = ProtocolServer(vm)
    created = server.handle({"id": 1, "command": "create_node", "type": "button", "node_id": "save_button"})
    assert created["success"] is True
    node = created["result"]
    assert server.handle({"id": 2, "command": "set_property", "node": node, "property": "text", "value": "Save"})["success"]
    response = server.handle({"id": 3, "command": "get_node", "node": node})
    assert response["result"]["properties"]["text"] == "Save"


def test_json_compiled_scene_and_runtime_visual_state():
    source = '{"page":{"id":"main","children":[{"type":"sprite","id":"hero","classes":["actor","selected"],"tags":["player"],"image":"assets/hero.png","animations":{"hover":{"scale":{"from":1,"to":1.1}}},"states":{"visible":true},"components":[{"type":"ShaderSprite","shader":"hologram","uniforms":{"strength":0.7}}]}]}}'
    compiled = Compiler().compile_scene(source, source_format="json")
    assert compiled.node_count == 2
    vm = SugiVM()
    vm.execute(compiled.program)
    hero = vm.query(".selected")[0]
    assert vm.heap.get(hero).properties["source"] == "assets/hero.png"
    assert vm.heap.get(hero).states["visible"] is True
    vm.play_animation(hero, "hover")
    assert vm.heap.get(hero).variables["active_animation"]["name"] == "hover"


def test_vm_set_uniform_updates_shader_material_component():
    source = """
page:
  id: root
  children:
    - type: sprite
      id: water
      components:
        - type: ShaderMaterial
          vertex: assets/shaders/screen.vert
          fragment: assets/shaders/water.frag
          uniforms:
            speed: 0.3
"""
    vm = SugiVM()
    vm.execute(Compiler().compile_yaml(source))
    water = vm.query("#water")[0]
    vm.set_uniform(water, "speed", 0.8)
    component = vm.heap.get(water).components[0]
    assert component.values["uniforms"]["speed"] == 0.8
