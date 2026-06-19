# Sugi

SUGI (Scene UI Graph Interface) is a language-agnostic UI virtual machine prototype. YAML is treated only as a source language; compiled applications run as SUGI bytecode against a DOM heap and expose behavior through a transport-independent protocol.

## Repository layout

- `sugi/` - initial working Python implementation of the compiler, bytecode, VM, protocol dispatcher, DOM heap, and render tree builder.
- `compiler/`, `runtime/`, `renderer/`, `protocol/` - subsystem boundaries for future adapters and implementations.
- `sdk/` - generated thin protocol wrappers will live here.
- `examples/` - source-language examples.
- `tests/` - subsystem and vertical-slice tests.
- `tools/` - developer tooling.
- `docs/` - architecture notes and diagrams.

## Current vertical slice

The project can compile a SUGI YAML page into binary `.sbc` bytecode, execute it inside the VM, mutate/query the DOM heap through protocol messages, dispatch browser-style events, and generate backend-independent render trees.

```bash
pytest -q
```
