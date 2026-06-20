#version 300 es
precision mediump float;
in vec2 v_uv;
out vec4 out_color;
uniform float iTime;
uniform vec3 iResolution;
void main() {
  vec2 uv = v_uv;
  float wave = sin((uv.x + iTime * 0.1) * 24.0) * 0.03;
  vec3 color = mix(vec3(0.02, 0.12, 0.22), vec3(0.0, 0.55, 0.8), uv.y + wave);
  out_color = vec4(color, 1.0);
}
