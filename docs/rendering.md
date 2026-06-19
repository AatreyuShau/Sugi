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


## Application boundary

Applications must not issue backend drawing calls. They create nodes, mutate properties or variables, attach scenes, and trigger animations. A backend calls `SceneRenderer.render(vm)` or `SceneRenderer.present(vm)` to traverse the DOM and produce a full frame.

```python
vm.set_property(player, "x", 100)
vm.set_property(player, "color", "#ff0000")
frame = SceneRenderer().render(vm)
```

## Built-in visual nodes

The reference renderer recognizes `page`, `panel`, `container`, `sprite`, `image`, `text`, `button`, `canvas`, `viewport`, `particle_system`, and `shader_surface`. Unknown node types remain safe scene-graph data for future renderer extensions.

Particle systems are renderer-owned. Applications mutate high-level parameters such as `effect`, `density`, `speed`, and `wind`; the renderer expands those values into particles for `rain`, `snow`, `leaves`, `dust`, `embers`, and `sparks`.

Shader surfaces are renderer-owned high-level effects. Applications mutate parameters such as `shader` and `strength`; renderer backends map effects like `water`, `fog`, `blur`, `glow`, `heat_distortion`, `crt`, and `pixelate` to the backend implementation.
