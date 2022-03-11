#version 330 core

layout(location = 0) in vec3 position;

uniform mat4 model, view, projection;

out vec3 tex_coords_back;
out vec3 tex_coords_front;

void main() {
    vec4 projected = projection * mat4(mat3(view)) * vec4(position, 1.0);
    gl_Position = projected.xyww;

    tex_coords_back = position;
    tex_coords_front = vec3(model * vec4(position, 0.0));
}
