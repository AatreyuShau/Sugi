# Tunnel Runner 3D-ish Demo

A lightweight pseudo-3D canvas demo that uses a SUGI scene description for the runner, obstacles, and collectible ring. The frontend projects lane/z game objects into perspective-scaled canvas shapes to demonstrate how SUGI-authored scene data can feed a game-style renderer.

## Run

From the repository root:

```bash
python tools/export_render_tree.py examples/tunnel_runner_3d/scene.yaml examples/tunnel_runner_3d/render_tree.json
python -m http.server 8001 --directory examples/tunnel_runner_3d
```

Open <http://localhost:8001>. Use `A/D` or `←/→` to switch lanes and avoid gates.

## Test

```bash
pytest -q tests/test_demo_scenes.py
```

## Showcase coverage

The tunnel runner demo highlights shader-style render commands, postprocess-like visual composition, and a static render tree that a web frontend can execute without owning scene logic.
