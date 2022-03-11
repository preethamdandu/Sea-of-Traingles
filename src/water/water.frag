#version 330 core

#define SHADOW_OFFSET_SCALE 0.001

const vec3 k_a = vec3(0.00, 0.30, 0.40);

flat in vec3 diffuse_specular;
in vec3 shadow_frag_pos;

uniform sampler2DShadow shadow_map;

out vec4 out_color;

vec3 fromLinear(vec3 color) {
    return pow(color, vec3(1.0 / 2.2));
}

float shadowFactor(vec3 shadow_frag_pos) {
    vec3 shadow_coords = 0.5 * shadow_frag_pos + 0.5;

    float factor = 0.0;
    for (float i = -1.5; i <= 1.5; i += 1.0) {
        for (float j = -1.5; j <= 1.5; j += 1.0) {
            vec2 offset = vec2(j, i) * SHADOW_OFFSET_SCALE;
            vec3 coords = vec3(shadow_coords.st + offset, shadow_coords.z);
            factor += texture(shadow_map, coords);
        }
    }

    return factor / 16.0;
}

void main() {
    float shadow = mix(0.5, 1.0, shadowFactor(shadow_frag_pos));

    vec3 color = k_a + shadow * diffuse_specular;

    out_color = vec4(fromLinear(color), 1.0);
}
