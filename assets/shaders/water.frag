#version 300 es
precision mediump float;
in vec2 v_uv;
out vec4 out_color;
uniform float time;
uniform float amplitude;
void main() {
  float wave = sin(v_uv.x * 28.0 + time) * amplitude;
  vec3 deep = vec3(0.02, 0.22, 0.36);
  vec3 foam = vec3(0.35, 0.91, 0.98);
  out_color = vec4(mix(deep, foam, smoothstep(0.45, 0.5, v_uv.y + wave)), 0.86);
}
