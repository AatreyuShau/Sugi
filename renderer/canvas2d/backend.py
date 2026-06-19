from sugi.visual_renderer import RenderFrame

def serialize_for_canvas(frame: RenderFrame) -> dict:
    return {"width": frame.width, "height": frame.height, "page_height": frame.page_height, "commands": frame.commands}
