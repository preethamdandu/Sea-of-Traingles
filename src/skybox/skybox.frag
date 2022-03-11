#version 330 core

in vec3 tex_coords_back;
in vec3 tex_coords_front;

uniform samplerCube tex_back;
uniform samplerCube tex_front;

out vec4 out_color;

void main() {
    vec3 back = texture(tex_back, tex_coords_back).rgb;
    vec4 front = texture(tex_front, tex_coords_front);

    out_color = vec4(mix(back, front.rgb, front.a), 1.0);
}
