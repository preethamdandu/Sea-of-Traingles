#version 330 core

#define NB_MAX_POINT_LIGHTS 8

#define SHADOW_BIAS 0.005
#define SHADOW_MAX_BIAS 0.01
#define SHADOW_OFFSET_SCALE 0.00125

in vec3 w_position;
in vec3 w_normal;
in vec3 shadow_frag_pos;

uniform int nb_point_lights;

uniform struct PointLight {
    vec3 position;
    vec3 color_intensity;
} point_lights[NB_MAX_POINT_LIGHTS];

uniform struct DirectionalLight {
    vec3 direction;
    vec3 color_intensity;
} directional_light;

uniform sampler2DShadow shadow_map;

uniform vec3 k_a;
uniform vec3 k_d;
uniform vec3 k_s;
uniform float s;

uniform vec3 w_camera_position;

out vec4 out_color;

vec3 fromLinear(vec3 color) {
    return pow(color, vec3(1.0 / 2.2));
}

vec3 pointLight(PointLight light, vec3 n, vec3 v) {
    vec3 l = light.position - w_position;
    float inv_dist_squared = 1.0 / dot(l, l);
    l = normalize(l);
    vec3 r = reflect(-l, n);

    float diffuse_coeff = max(dot(n, l), 0.0);
    vec3 diffuse = k_d * diffuse_coeff;

    float specular_coeff = pow(max(dot(r, v), 0.0), s);
    vec3 specular = k_s * specular_coeff;

    return light.color_intensity * (diffuse + specular) * inv_dist_squared;
}

vec3 directionalLight(DirectionalLight light, vec3 n, vec3 v) {
    vec3 l = normalize(-light.direction);
    vec3 r = reflect(-l, n);

    float diffuse_coeff = max(dot(n, l), 0.0);
    vec3 diffuse = k_d * diffuse_coeff;

    float specular_coeff = pow(max(dot(r, v), 0.0), s);
    vec3 specular = k_s * specular_coeff;

    return light.color_intensity * (diffuse + specular);
}

float shadowFactor(vec3 shadow_frag_pos, vec3 n, vec3 l) {
    vec3 shadow_coords = 0.5 * shadow_frag_pos + 0.5;

    float NdotL = dot(n, l);
    float bias = SHADOW_BIAS * sqrt(max(1.0 - NdotL * NdotL, 0.0)) / NdotL;
    shadow_coords.z -= clamp(bias, 0.0, SHADOW_MAX_BIAS);

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
    vec3 n = normalize(w_normal);
    vec3 v = normalize(w_camera_position - w_position);

    vec3 color = directionalLight(directional_light, n, v);

    for (int i = 0; i < nb_point_lights && i < NB_MAX_POINT_LIGHTS; ++i) {
        color += pointLight(point_lights[i], n, v);
    }

    vec3 l = normalize(-directional_light.direction);
    float shadow = mix(0.6, 1.0, shadowFactor(shadow_frag_pos, n, l));
    color = k_a + shadow * color;

    out_color = vec4(fromLinear(color), 1.0);
}
