#version 300 es
precision mediump float;
in vec2 v_uv;
out vec4 out_color;
uniform float time;
void main() {
  vec3 dawn = vec3(0.03, 0.19, 0.38);
  vec3 dusk = vec3(0.45, 0.16, 0.72);
  float band = 0.5 + 0.5 * sin((v_uv.x + time * 0.04) * 8.0 + v_uv.y * 4.0);
  out_color = vec4(mix(dawn, dusk, band) + vec3(0.05 * v_uv.y), 1.0);
}
