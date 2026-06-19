# SUGI Ui Demo Showcase

This demo showcases SUGI visual ownership for `ui_demo` while applications only mutate VM/protocol state.

## Run

```bash
python tools/export_render_tree.py examples/ui_demo/scene.yaml examples/ui_demo/web/render_tree.json
python examples/ui_demo/native/ui_demo_native.py
```

Open `examples/ui_demo/web/index.html` from a static server to view the web frontend. The web and native frontends consume the same SUGI scene/render tree and do not own business logic.
