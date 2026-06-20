# Building SUGI scenes and render trees

SUGI separates application logic from rendering:

```text
YAML scene → Compiler → VM DOM → RenderTree/RenderFrame → Renderer backend
```

Applications should mutate VM state (`set_variable`, `set_property`, `call`) and then ask a renderer to render the VM or an exported render tree. Applications should not draw water, gradients, sprites, or shader rectangles themselves.

## YAML scene format

A scene has a `materials` table and a `page` root:

```yaml
materials:
  water:
    vertex: shaders/screen.vert
    fragment: shaders/water.frag
    uniforms:
      iTime: auto
      iResolution: auto
page:
  id: my_scene
  width: 800
  height: 450
  children:
    - type: surface
      id: water_surface
      material: water
      x: 0
      y: 0
      width: 800
      height: 450
```

Supported node fields include:

- `type`, `id`, `children`
- geometry: `x`, `y`, `width`, `height`, `parallax`
- sprite image paths: `image` or `source`
- materials: `material`
- text: `text`, `font_size`, `color`
- app state: `variables`, `components`, `events`, `animations`, `classes`, `tags`

Supported material fields:

- `vertex`: path to a custom vertex shader
- `fragment`: path to a custom fragment shader
- `uniforms`: explicit values or `auto`
- `shadertoy: true`: wrap a `mainImage(out vec4 fragColor, in vec2 fragCoord)` fragment for renderer use

Automatic uniforms currently include `iTime`, `iResolution`, `iMouse`, `iFrame`, `cameraPosition`, and `viewportSize`. The renderer updates these; application code does not.

## Render tree format

`tools/export_render_tree.py` serializes the VM DOM for static frontends. A render tree is JSON with root nodes shaped like:

```json
{
  "handle": 1,
  "type": "page",
  "id": "my_scene",
  "properties": {
    "width": 800,
    "height": 450,
    "__materials": {
      "water": {
        "vertex": "shaders/screen.vert",
        "fragment": "shaders/water.frag",
        "uniforms": { "iTime": "auto" },
        "shadertoy": false
      }
    }
  },
  "components": [],
  "children": []
}
```

The `__materials` map is required for static web/native frontends because those frontends do not run the compiler. It tells the renderer which shader files to fetch/compile and which uniforms belong to each material. If an app embeds Python and runs the compiler directly, it can render from the VM without a JSON file.

## Why a render tree is required for web demos

Browsers served from static files cannot import the Python compiler or VM. The render tree is the compiled, language-neutral handoff format:

1. Python compiles YAML into VM DOM.
2. The exporter serializes DOM nodes and material metadata.
3. The browser loads the JSON and renders it with WebGL.

This keeps YAML as the source of truth while allowing static hosting.

## Developing your own scene

1. Create `my_scene.yaml` with `materials` and a `page` tree.
2. Put images under `assets/images` or next to your demo.
3. Put shaders under your demo or `assets/shaders`.
4. Export for web:

   ```bash
   python tools/export_render_tree.py my_scene.yaml my_demo/render_tree.json
   ```

5. In web, load `examples/shared/sugi-webgl-renderer.js` and call `renderer.loadScene(renderTree)` followed by `renderer.render()` each frame.
6. In Python native demos, run the compiler/VM and give `RenderTreeBuilder().build(vm)` to `NativeCanvasRenderer` or a production native GPU backend.
