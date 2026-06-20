#version 300 es
precision mediump float;
in vec2 v_uv;
out vec4 out_color;
uniform float strength;
void main() {
  float scan = step(0.55, fract(v_uv.y * 24.0));
  out_color = vec4(1.0, 0.82 + scan * 0.18, 0.12, 0.8 + strength * 0.2);
}
