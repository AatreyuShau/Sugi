#version 300 es
precision mediump float;
in vec2 a_position;
out vec2 v_uv;
uniform vec4 u_rect;
uniform vec2 u_viewport;
void main() {
  v_uv = a_position * 0.5 + 0.5;
  vec2 pixel = u_rect.xy + v_uv * u_rect.zw;
  vec2 clip = pixel / u_viewport * 2.0 - 1.0;
  gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0);
}
