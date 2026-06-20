# SUGI Water Shader Demo

This demo shows the intended SUGI flow for custom materials:

```text
water.yaml → Compiler → VM DOM → RenderTree → Renderer → GPU/native backend
```

## Files

- `water.yaml` declares a `water` material with a custom vertex shader and fragment shader.
- `shaders/screen.vert` maps a SUGI rectangle into clip space using `u_rect` and `u_viewport`.
- `shaders/water.frag` is the user-owned fragment shader. SUGI supplies automatic uniforms such as `iTime` and `iResolution`.
- `index.html` runs the web demo with the shared WebGL renderer.
- `native/water_native.py` runs the same YAML through the Python VM and native Tk debug renderer.
- `render_tree.json` is the exported VM render tree used by static web hosting.

## Run

From the repository root:

```bash
python tools/export_render_tree.py examples/shader_water/water.yaml examples/shader_water/render_tree.json
python -m http.server 8000
# open http://localhost:8000/examples/shader_water/
```

Native debug backend:

```bash
python examples/shader_water/native/water_native.py
```

The native Tk backend is for local app development and debugging. Production native rendering is expected to use the same material metadata with an OpenGL/Vulkan/Metal/DirectX backend.
