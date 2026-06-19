# Sugi

SUGI (Scene UI Graph Interface) is a language-agnostic UI virtual machine prototype. YAML is treated only as a source language; compiled applications run as SUGI bytecode against a DOM heap and expose behavior through a transport-independent protocol.

## Repository layout

- `sugi/` - initial working Python implementation of the compiler, bytecode, VM, protocol dispatcher, DOM heap, and render tree builder.
- `compiler/`, `runtime/`, `renderer/`, `protocol/` - subsystem boundaries for future adapters and implementations.
- `sdk/` - generated thin protocol wrappers will live here.
- `examples/` - source-language examples, including a shared SUGI platformer scene with web and native frontends.
- `tests/` - subsystem and vertical-slice tests.
- `tools/` - developer tooling.
- `docs/` - architecture notes and diagrams.

## Current vertical slice

The project can compile a SUGI YAML page into binary `.sbc` bytecode, execute it inside the VM, mutate/query the DOM heap through protocol messages, dispatch browser-style events, and generate backend-independent render trees.

```bash
pytest -q
```

## Platformer example

See `examples/platformer/README.md` for a shared SUGI scene that can be exported to a browser canvas app or run directly in a native Tk desktop window.

Additional demos:

- `examples/tunnel_runner_3d/README.md` shows a pseudo-3D canvas game driven by exported SUGI scene data.
- `examples/login_canvas/README.md` shows a canvas-only browser login where Python owns interactions and rendering state.
