#version 300 es
precision mediump float;
in vec2 v_uv;
out vec4 out_color;
uniform sampler2D scene_texture;
void main() {
  vec4 c = texture(scene_texture, v_uv);
  out_color = vec4(c.rgb + max(c.rgb - vec3(0.7), vec3(0.0)) * 0.25, c.a);
}
