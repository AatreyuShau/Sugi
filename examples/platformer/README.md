# SUGI Platformer Example

This example uses one SUGI source scene, `platformer.yaml`, for two runnable frontends:

- `web/index.html` renders the scene on a full-screen HTML canvas with no HTML widgets.
- `native/platformer_native.py` renders the same scene in a native desktop window using Python's standard-library Tk canvas.

Both frontends treat the YAML file as source input only. The shared run path is:

```text
platformer.yaml -> SUGI bytecode -> SugiVM DOM heap -> render tree -> backend adapter
```

## Run the web app

From the repository root:

```bash
python tools/export_render_tree.py examples/platformer/platformer.yaml examples/platformer/web/render_tree.json
python -m http.server 8000 --directory examples/platformer/web
```

Open <http://localhost:8000> in a browser.

Controls: `A/D` or `←/→` to move, `W`, `Space`, or `↑` to jump. Reach the gold door.

## Run the native app

From the repository root:

```bash
python examples/platformer/native/platformer_native.py
```

The native app compiles `platformer.yaml` to SUGI bytecode at startup, executes it in the VM, builds a render tree, and draws it in a Tk window.

## Test the example

```bash
pytest -q
python -m compileall sugi examples/platformer/native tools
python tools/export_render_tree.py examples/platformer/platformer.yaml /tmp/platformer_render_tree.json
```

## Showcase coverage

This demo is intentionally application-driven: keyboard input and collision remain in the frontend, while the shared SUGI scene defines the page, sprites, solids, goal component, text, and render tree consumed by both web and native frontends.
## Material platformer update

The platformer now showcases a horizontal scrolling SUGI scene: the player is declared as an image sprite, the sky/cloud/water/gate layers are backed by application-supplied materials, the camera follows the player on the x-axis, and both web and native frontends consume the same SUGI scene data while keeping input and collision as application logic.
