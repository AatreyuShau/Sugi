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
