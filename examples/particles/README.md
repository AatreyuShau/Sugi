# SUGI Particles Showcase

This demo showcases SUGI visual ownership for `particles` while applications only mutate VM/protocol state.

## Run

```bash
python tools/export_render_tree.py examples/particles/scene.yaml examples/particles/web/render_tree.json
python examples/particles/native/particles_native.py
```

Open `examples/particles/web/index.html` from a static server to view the web frontend. The web and native frontends consume the same SUGI scene/render tree and do not own business logic.
