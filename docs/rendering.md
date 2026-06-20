# Render capabilities

SUGI renderers consume VM DOM/render-tree nodes and interpret materials, sprites, text, and scene geometry. The VM stores scene state; it does not draw and it does not decide what visual effects exist.

## Materials and shaders

Materials are declared in YAML and point at application-owned shader files:

```yaml
materials:
  water:
    vertex: assets/shaders/screen.vert
    fragment: assets/shaders/water.frag
    uniforms:
      iTime: auto
      iResolution: auto
```

Backends compile/cache shaders, bind uniforms, and draw nodes that reference `material: water`. SUGI does not ship hidden water/cloud/aurora effects; those effects exist only as user shader assets.

## Image sprites

Sprite nodes can reference image assets with `image` or `source`:

```yaml
- type: sprite
  id: player
  image: assets/images/hero.svg
  x: 96
  y: 364
  width: 52
  height: 64
```

Backends load/cache/upload images and draw textured quads. Supported image path extensions are PNG, JPG/JPEG, WEBP, and SVG.

## Render trees

Static frontends use exported render trees so they can render compiled VM DOM state without embedding the Python compiler. See `docs/rendering_pipeline.md` for the full format and rationale.

## Application boundary

Applications must not issue backend drawing calls. They create nodes, mutate properties/variables/uniforms, dispatch events, and trigger animations. A backend calls the renderer to traverse the DOM/render tree and produce a frame.

```python
vm.set_property(player, "x", 100)
renderer.render(vm)
```

## Renderable nodes

The current demo renderers support `page`, `surface`, `shader_surface`, `sprite`, `image`, `platform`, and `text` nodes, with material metadata supplied through the VM/render tree.
