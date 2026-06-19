# Sugi

SUGI (Scene UI Graph Interface) is a language-agnostic UI virtual machine prototype. YAML is treated only as a source language; compiled applications run as SUGI bytecode against a DOM heap and expose behavior through a transport-independent protocol.

## Repository layout

- `sugi/` - initial working Python implementation of the compiler, bytecode, VM, protocol dispatcher, DOM heap, and render tree builder.
- `compiler/`, `runtime/`, `renderer/`, `protocol/` - subsystem boundaries for future adapters and implementations.
- `sdk/` - generated thin protocol wrappers will live here.
- `examples/` - source-language examples, including a shared SUGI platformer scene with web and native frontends.
- `tests/` - subsystem and vertical-slice tests.
- `tools/` - developer tooling.
- `docs/` - architecture notes, rendering capabilities, and diagrams.

## Current vertical slice

The project can compile a SUGI YAML page into binary `.sbc` bytecode, execute it inside the VM, mutate/query the DOM heap through protocol messages, dispatch browser-style events, generate backend-independent render trees, and render full frames from scene state via `SceneRenderer.render(vm)`.

```bash
pytest -q
```

## Platformer example

See `examples/platformer/README.md` for a shared SUGI scene that can be exported to a browser canvas app or run directly in a native Tk desktop window.

Additional demos:

- `examples/portfolio_template/README.md` shows a polished Python-driven canvas portfolio with scroll lock, mouse trails, pen layers, full-frame shaders, and shader/image sprites.
- `examples/login_canvas/README.md` shows a canvas-only browser login where Python owns interactions and rendering state.
