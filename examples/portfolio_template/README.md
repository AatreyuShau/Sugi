# Polished Portfolio Template

This replaces the removed 3D runner with a portfolio-style canvas page that showcases richer SUGI render concepts:

- Full-frame shader nodes (`FullFrameShader`) for aurora/grid backgrounds.
- Per-node sprite rendering (`ImageSprite`) with per-sprite shader overlays (`ShaderSprite`).
- Pen layers (`PenLayer`) for mouse trails and drawn ribbon effects.
- A scroll-locked middle storytelling section.
- Interactive background parallax, mouse trails, and scroll-reactive cards.

## Run

From the repository root:

```bash
python tools/export_render_tree.py examples/portfolio_template/portfolio.yaml examples/portfolio_template/web/render_tree.json
python -m http.server 8002 --directory examples/portfolio_template/web
```

Open <http://localhost:8002>.

## Test

```bash
pytest -q tests/test_portfolio_template.py
```
