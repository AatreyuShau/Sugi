#version 330 core
uniform float iTime;
uniform vec3 iResolution;
in vec2 vUv;
out vec4 fragColor;
void main() {
    vec2 uv = vUv;
    float wave = sin((uv.x + iTime * 0.1) * 24.0) * 0.03;
    vec3 color = mix(vec3(0.02, 0.12, 0.22), vec3(0.0, 0.55, 0.8), uv.y + wave);
    fragColor = vec4(color, 1.0);
}
