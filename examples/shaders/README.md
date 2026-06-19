# SUGI Shaders Showcase

This demo showcases SUGI visual ownership for `shaders` while applications only mutate VM/protocol state.

## Run

```bash
python tools/export_render_tree.py examples/shaders/scene.yaml examples/shaders/web/render_tree.json
python examples/shaders/native/shaders_native.py
```

Open `examples/shaders/web/index.html` from a static server to view the web frontend. The web and native frontends consume the same SUGI scene/render tree and do not own business logic.
