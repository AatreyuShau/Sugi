# Render Capabilities

SUGI renderers consume render-tree nodes and interpret components. The VM stores components but does not render them.

## Sprite nodes

Any render node can be treated as an isolated sprite surface by renderer backends. The portfolio template demonstrates:

- `ImageSprite` for image-backed node rendering.
- `ShaderSprite` for applying a shader-like material to one node only.
- Plain `Sprite` for generated cards, glass panels, and composited surfaces.

## Full-frame shader nodes

`FullFrameShader` marks a node as a viewport or large-surface procedural pass. Backends can map this to WebGL, a native GPU pipeline, a software shader, or a canvas approximation. The HTML portfolio demo implements canvas approximations for aurora and grid-warp passes.

## Pen layers

`PenLayer` marks a node as a retained drawing surface for strokes, trails, signatures, ribbons, and brush effects. Backends can implement this as vector paths, CPU raster strokes, or GPU line/particle passes.

These capabilities stay renderer-owned: bytecode and VM execution only preserve the component data, stable handles, properties, variables, and render-tree ordering.
