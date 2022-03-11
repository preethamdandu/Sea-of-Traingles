#version 330 core

#define POSITION_SCALING_FACTOR 0.25
#define TIME_SCALING_FACTOR 0.25

layout(location = 0) in vec2 position;
layout(location = 1) in float axis;

uniform mat4 view, projection;
uniform mat4 shadow_viewproj;

uniform float time;

uniform vec3 w_camera_position;

flat out vec3 diffuse_specular;
out vec3 shadow_frag_pos;

/** Simplex Noise
 * from "Efficient computational noise in GLSL" by Ian McEwan et al.
 * https://github.com/ashima/webgl-noise/blob/master/src/noise3D.glsl
 */

vec3 mod289(vec3 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 mod289(vec4 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 permute(vec4 x) {
    return mod289(((x * 34.0) + 1.0) * x);
}

vec4 taylorInvSqrt(vec4 r)
{
    return 1.79284291400159 - 0.85373472095314 * r;
}

float snoise(vec3 v)
{
    const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

    // First corner
    vec3 i = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);

    // Other corners
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);

    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;

    // Permutations
    i = mod289(i);
    vec4 p = permute(permute(permute(
            i.z + vec4(0.0, i1.z, i2.z, 1.0))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0));

    // Gradients: 7x7 points over a square, mapped onto an octahedron.
    // The ring size 17*17 = 289 is close to a multiple of 49 (49*6 = 294)
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;

    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);

    vec4 x = x_ * ns.x + ns.yyyy;
    vec4 y = y_ * ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);

    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);

    vec4 s0 = floor(b0) * 2.0 + 1.0;
    vec4 s1 = floor(b1) * 2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));

    vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;

    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);

    // Normalise gradients
    vec4 norm = taylorInvSqrt(vec4(dot(p0, p0), dot(p1, p1), dot(p2, p2), dot(p3, p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;

    // Mix final noise value
    vec4 m = max(0.6 - vec4(dot(x0, x0), dot(x1, x1), dot(x2, x2), dot(x3, x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1), dot(p2, x2), dot(p3, x3)));
}

/* End of Simplex Noise */

float noise(vec3 x) {
    float sum = 0.0;
    float amplitude = 1.0;
    float frequency = 1.0;
    for (int i = 0; i < 4; ++i) {
        sum += amplitude * snoise(frequency * x);
        amplitude *= 0.5;
        frequency *= 2.0;
    }

    return sum / 1.875;
}

float height(vec2 position) {
    return noise(vec3(POSITION_SCALING_FACTOR * position, TIME_SCALING_FACTOR * time));
}

vec3 normal(vec3 position, float axis) {
    float hx = height(position.xz + vec2(axis, 0));
    vec3 ax = vec3(axis, hx - position.y, 0);

    float hz = height(position.xz + vec2(0, -axis));
    vec3 az = vec3(0, hz - position.y, -axis);

    return normalize(cross(ax, az));
}

/**
 * Fragment shader per vertex
 */

#define NB_MAX_POINT_LIGHTS 8

#define F0 0.02

const vec3 k_d = vec3(0.00, 0.50, 0.60);
const vec3 k_s = vec3(0.57, 0.57, 0.57);
const float s = 64.0;

uniform int nb_point_lights;

uniform struct PointLight {
    vec3 position;
    vec3 color_intensity;
} point_lights[NB_MAX_POINT_LIGHTS];

uniform struct DirectionalLight {
    vec3 direction;
    vec3 color_intensity;
} directional_light;

uniform samplerCube env_tex_back;
uniform samplerCube env_tex_front;
uniform mat4 env_rotation;

mat2x3 pointLight(PointLight light, vec3 w_position, vec3 n, vec3 v) {
    vec3 l = light.position - w_position;
    float inv_dist_squared = 1.0 / dot(l, l);
    l = normalize(l);
    vec3 r = reflect(-l, n);

    float diffuse_coeff = max(dot(n, l), 0.0);
    vec3 diffuse = k_d * diffuse_coeff * light.color_intensity * inv_dist_squared;

    float specular_coeff = pow(max(dot(r, v), 0.0), s);
    vec3 specular = k_s * specular_coeff * light.color_intensity * inv_dist_squared;

    return mat2x3(diffuse, specular);
}

mat2x3 directionalLight(DirectionalLight light, vec3 n, vec3 v) {
    vec3 l = normalize(-light.direction);
    vec3 r = reflect(-l, n);

    float diffuse_coeff = max(dot(n, l), 0.0);
    vec3 diffuse = k_d * diffuse_coeff * light.color_intensity;

    float specular_coeff = pow(max(dot(r, v), 0.0), s);
    vec3 specular = k_s * specular_coeff * light.color_intensity;

    return mat2x3(diffuse, specular);
}

vec3 environmentReflection(vec3 n, vec3 v) {
    vec3 r = reflect(-v, n);

    vec3 back = texture(env_tex_back, r).rgb;
    vec4 front = texture(env_tex_front, vec3(env_rotation * vec4(r, 0.0)));

    return mix(back, front.rgb, front.a);
}

vec3 fresnel(vec3 color_refract, vec3 color_reflect, vec3 n, vec3 v) {
    float NdotV = max(dot(n, v), 0.0);
    float schlick = F0 + (1.0 - F0) * pow(1.0 - NdotV, 5.0);

    return mix(color_refract, color_reflect, schlick);
}

vec3 fragment(vec3 w_position, vec3 w_normal) {
    vec3 n = w_normal;
    vec3 v = normalize(w_camera_position - w_position);

    mat2x3 colors = directionalLight(directional_light, n, v);
    for (int i = 0; i < nb_point_lights && i < NB_MAX_POINT_LIGHTS; ++i) {
        colors += pointLight(point_lights[i], w_position, n, v);
    }

    vec3 color_reflect = environmentReflection(n, v);
    vec3 f = fresnel(colors[0], color_reflect, n, v);

    return f + colors[1];
}

/* End of fragment shader per vertex */

void main() {
    vec2 xz_position = position + floor(w_camera_position.xz);
    vec3 w_position = vec3(xz_position.x, height(xz_position), xz_position.y);
    vec3 w_normal = normal(w_position, axis);
    gl_Position = projection * view * vec4(w_position, 1.0);

    shadow_frag_pos = vec3(shadow_viewproj * vec4(w_position, 1.0));

    diffuse_specular = fragment(w_position, w_normal);
}
