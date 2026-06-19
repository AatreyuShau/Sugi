#version 300 es
precision mediump float;
in vec2 v_uv;
out vec4 out_color;
uniform float time;
float stripe(float x) { return smoothstep(0.42, 0.5, sin(x) * 0.5 + 0.5); }
void main() {
  float n = stripe((v_uv.x + time * 0.02) * 22.0 + sin(v_uv.y * 9.0));
  out_color = vec4(vec3(0.65, 0.85, 1.0) * n, 0.28 * n);
}
