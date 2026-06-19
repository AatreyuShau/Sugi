from examples.login_canvas.server.login_server import LoginController


def test_login_controller_updates_vm_from_canvas_events():
    controller = LoginController()
    controller.handle_event({"type": "click", "x": 240, "y": 200})
    for key in "demo":
        controller.handle_event({"type": "key", "key": key})
    controller.handle_event({"type": "key", "key": "Tab"})
    for key in "sugi":
        controller.handle_event({"type": "key", "key": key})
    controller.handle_event({"type": "key", "key": "Enter"})
    status = controller.vm.heap.get(controller.status)
    assert status.properties["text"] == "Welcome to SUGI!"
    frame = controller.frame()
    assert any(command.get("text") == "Welcome to SUGI!" for command in frame["commands"])
