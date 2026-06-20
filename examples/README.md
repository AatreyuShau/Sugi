# SUGI examples

The repository now keeps only the supported end-to-end examples:

| Demo | Scene | Web | Native | Purpose |
| --- | --- | --- | --- | --- |
| Platformer | `platformer/platformer.yaml` | `platformer/web/index.html` | `platformer/native/platformer_native.py` | Gameplay mutates VM state while SUGI renders image sprites, material surfaces, and world geometry. |
| Water shader | `shader_water/water.yaml` | `shader_water/index.html` | `shader_water/native/water_native.py` | Minimal custom vertex/fragment material example. |
| Login page | `login_canvas/login.yaml` | `login_canvas/web/index.html` | `login_canvas/server/login_server.py` | VM-driven UI and input state without app-side drawing. |

Regenerate static web render trees with:

```bash
python tools/export_render_tree.py examples/platformer/platformer.yaml examples/platformer/web/render_tree.json
python tools/export_render_tree.py examples/shader_water/water.yaml examples/shader_water/render_tree.json
```

Login uses the server/controller flow in `examples/login_canvas/server/login_server.py`.
