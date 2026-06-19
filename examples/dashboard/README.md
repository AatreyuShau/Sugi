# SUGI Dashboard Showcase

This demo showcases SUGI visual ownership for `dashboard` while applications only mutate VM/protocol state.

## Run

```bash
python tools/export_render_tree.py examples/dashboard/scene.yaml examples/dashboard/web/render_tree.json
python examples/dashboard/native/dashboard_native.py
```

Open `examples/dashboard/web/index.html` from a static server to view the web frontend. The web and native frontends consume the same SUGI scene/render tree and do not own business logic.
