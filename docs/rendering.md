# Render Capabilities

SUGI renderers consume render-tree nodes and interpret components. The VM stores scene state; it does not draw and it does not decide what visual effects exist.

## Sprite nodes

Any render node can be treated as an isolated sprite surface by renderer backends. Sprites can carry image references, UV regions, transforms, opacity, tint, blend modes, or a `ShaderMaterial` component. Applications supply image files and shader/material files; SUGI caches and binds them.

## Shader materials

`ShaderMaterial` marks a node as a viewport, sprite, or large-surface pass backed by application-supplied GLSL/WGSL stages. Backends compile and cache those stages, bind uniforms, share compatible programs, batch compatible materials, and allocate render targets as needed. SUGI does not define built-in shader effects.

```yaml
components:
  - type: ShaderMaterial
    vertex: assets/shaders/screen.vert
    fragment: assets/shaders/water.frag
    uniforms:
      speed: 0.3
```

Applications may mutate uniforms through the VM; the renderer updates GPU state during presentation.

```python
vm.set_uniform(water_node, "speed", 0.8)
```

## Pen layers

`PenLayer` marks a retained drawing surface for polylines, strokes, trails, signatures, ribbons, and brush data. Applications provide points or high-level stroke parameters. Renderer backends turn that retained data into vector paths, CPU raster strokes, or GPU line buffers.

## Particles

Particle systems are generic renderer-owned draw streams. Applications define texture references, lifetimes, velocities, spawn rates, and curves. SUGI performs rendering and resource reuse, but it does not ship predefined effects as application behavior.

## Application boundary

Applications must not issue backend drawing calls. They create nodes, mutate properties/variables/uniforms, dispatch events, and trigger animations. A backend calls `SceneRenderer.render(vm)` or `SceneRenderer.present(vm)` to traverse the DOM and produce a full frame.

```python
vm.set_property(player, "x", 100)
vm.set_uniform(water, "amplitude", 0.2)
frame = SceneRenderer().render(vm)
```

## Renderable nodes

The reference renderer recognizes `page`, `panel`, `container`, `sprite`, `image`, `text`, `button`, `canvas`, `viewport`, `particle_system`, `pen`, and `shader_surface`. Unknown node types remain safe scene-graph data for future renderer extensions.
