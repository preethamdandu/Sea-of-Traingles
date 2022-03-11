#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

uniform mat4 model, view, projection;
uniform mat4 normal_matrix;
uniform mat4 shadow_viewproj;

out vec3 w_position;
out vec3 w_normal;
out vec3 shadow_frag_pos;

void main() {
    vec4 model_position = model * vec4(position, 1.0);
    w_position = vec3(model_position) / model_position.w;
    gl_Position = projection * view * model_position;

    w_normal = normalize(vec3(normal_matrix * vec4(normal, 0.0)));

    shadow_frag_pos = vec3(shadow_viewproj * vec4(w_position, 1.0));
}
