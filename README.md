# Sugi

SUGI (Scene UI Graph Interface) is a language-agnostic UI virtual machine prototype. YAML is a source language; compiled applications run as SUGI bytecode against a DOM heap and render through backend-owned renderers.

## Repository layout

- `sugi/` - Python compiler, bytecode, VM, protocol dispatcher, DOM heap, render tree builder, and debug native renderer.
- `compiler/`, `runtime/`, `renderer/`, `protocol/` - subsystem boundaries for parsers, ASTs, validators, render commands, backend adapters, GPU resources, textures, and protocol wrappers.
- `sdk/` - thin protocol wrappers for Python, Rust, Go, C#, Java, and JavaScript.
- `assets/` - backend-independent image, shader, material, and font assets.
- `examples/` - supported end-to-end examples: platformer, water shader, and login page.
- `docs/` - architecture and rendering notes, including `docs/rendering_pipeline.md` for scene/render-tree authoring.

## Current vertical slice

The project can compile SUGI YAML or JSON pages into bytecode or a `CompiledScene`, execute them inside the VM, mutate/query DOM state, generate render trees with material metadata, and render via web/native demo renderers.

```bash
pytest -q
```

## Examples

- `examples/platformer/README.md` - image sprite player, material sky/water/hologram surfaces, web and native frontends.
- `examples/shader_water/README.md` - minimal custom vertex/fragment water material, web and native frontends.
- `examples/login_canvas/README.md` - VM-driven login UI and input state.

## Developing your own scene

Start with `docs/rendering_pipeline.md`. It explains YAML scene structure, supported render-tree fields, why static web demos need exported render trees, and how to connect custom shaders/images to renderer backends.
