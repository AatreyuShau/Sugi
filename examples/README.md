# SUGI demos and feature showcases

Every demo follows the core SUGI rule: application code owns logic and mutates VM/protocol state; SUGI owns the scene graph, visual components, rendering commands, assets, shaders, particles, text, and layout.

| Demo | Scene | Web frontend | Native/frontend | Feature coverage |
| --- | --- | --- | --- | --- |
| Platformer | `platformer/platformer.yaml` | `platformer/web/index.html` | `platformer/native/platformer_native.py` | DOM nodes, sprites, camera-like world view, event-driven app logic outside SUGI |
| Portfolio template | `portfolio_template/portfolio.yaml` | `portfolio_template/web/index.html` | Python server frontend | scroll lock, pen trails, shader surfaces, image/shader sprites, text |
| Login canvas | `login_canvas/login.yaml` | `login_canvas/web/index.html` | Python server frontend | protocol-style input relay, text input components, declarative UI |
| Tunnel runner 3D | `tunnel_runner_3d/scene.yaml` | `tunnel_runner_3d/index.html` | shared render tree | shader/postprocess-style tunnel visuals |
| UI demo | `ui_demo/scene.yaml` | `ui_demo/web/index.html` | `ui_demo/native/ui_demo_native.py` | layout, buttons, text, events, animations, scroll regions |
| Particles | `particles/scene.yaml` | `particles/web/index.html` | `particles/native/particles_native.py` | particle emitters, wind/gravity/lifetime parameters, pen layers |
| Shaders | `shaders/scene.yaml` | `shaders/web/index.html` | `shaders/native/shaders_native.py` | application GLSL materials, postprocess, render targets, uniforms |
| Image gallery | `image_gallery/scene.yaml` | `image_gallery/web/index.html` | `image_gallery/native/image_gallery_native.py` | cached images, SVG/PNG/JPEG/WEBP references, UVs, nine-slice, blend modes |
| Dashboard | `dashboard/scene.yaml` | `dashboard/web/index.html` | `dashboard/native/dashboard_native.py` | protocol subscriptions, dashboard state, camera, grid layout, components |

Regenerate static render trees with:

```bash
for ex in ui_demo particles shaders image_gallery dashboard; do \
  python tools/export_render_tree.py examples/$ex/scene.yaml examples/$ex/web/render_tree.json; \
done
```
