# SUGI Image Gallery Showcase

This demo showcases SUGI visual ownership for `image_gallery` while applications only mutate VM/protocol state.

## Run

```bash
python tools/export_render_tree.py examples/image_gallery/scene.yaml examples/image_gallery/web/render_tree.json
python examples/image_gallery/native/image_gallery_native.py
```

Open `examples/image_gallery/web/index.html` from a static server to view the web frontend. The web and native frontends consume the same SUGI scene/render tree and do not own business logic.
