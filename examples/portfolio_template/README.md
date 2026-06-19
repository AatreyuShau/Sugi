# Polished Portfolio Template

This replaces the removed 3D runner with a portfolio-style canvas page that showcases richer SUGI render concepts. Python owns the SUGI VM, stores relayed web information in DOM variables, computes the frame commands, and the browser only relays viewport/mouse/scroll state plus paints those commands to canvas:

- Full-frame shader nodes (`FullFrameShader`) for aurora/grid backgrounds.
- Per-node sprite rendering (`ImageSprite`) with per-sprite shader overlays (`ShaderSprite`).
- Pen layers (`PenLayer`) for mouse trails and drawn ribbon effects.
- A scroll-locked middle storytelling section.
- Interactive background parallax, mouse trails, and scroll-reactive cards.

## Run

From the repository root:

```bash
python examples/portfolio_template/server/portfolio_server.py
```

Open <http://localhost:8766>.

## Test

```bash
pytest -q tests/test_portfolio_template.py
python -m compileall examples/portfolio_template/server
```

## Showcase coverage

The portfolio demo exercises scroll variables, scroll lock components, shader surfaces, shader/image sprites, pen layers, wrapped text, mouse trails, and Python-owned state mutation with SUGI-owned rendering.
