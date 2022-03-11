#!/usr/bin/env python3

from math import sqrt

import OpenGL.GL as GL

from core.shader import Shader
from core.mesh import Mesh
from water.noise import vec3, noise


RADIUS = 160
VERTEX_SHADER_NAME = 'water/water.vert'
FRAGMENT_SHADER_NAME = 'water/water.frag'
POSITION_SCALING_FACTOR = 0.25
TIME_SCALING_FACTOR = 0.25


class Water(Mesh):
    def __init__(self, lights_manager, skybox):
        self.lights_manager = lights_manager
        self.skybox = skybox

        shader = Shader(VERTEX_SHADER_NAME, FRAGMENT_SHADER_NAME)
        self.lights_manager.add_shader(shader)

        position = []
        axis = []
        x_ranges = []
        for z in range(-RADIUS + 1, RADIUS):
            x_range = int(sqrt(RADIUS * RADIUS - z * z))
            x_ranges.append(x_range)
            for x in range(-x_range, x_range + 1):
                position.append((x, z))
                axis.append((-1,))
                position.append((x, z + 1))
                axis.append((1,))

        index = []
        z_offset = 0
        for x_range in x_ranges:
            for x in range(-x_range, x_range):
                offset = z_offset + 2 * (x + x_range)
                index += [offset + 1, offset + 3, offset, offset + 2, offset, offset + 3]

            z_offset += 2 * (2 * x_range + 1)

        super().__init__(shader, (position, axis), index)

        self.add_locations('time', 'w_camera_position', 'env_tex_back', 'env_tex_front', 'env_rotation')

        self.current_time = 0

    def update(self, delta_time):
        self.current_time += delta_time

    def draw(self, projection, view, model, normal_matrix, camera):
        GL.glUseProgram(self.shader.glid)

        GL.glUniform1f(self.locations['time'], self.current_time)

        self.lights_manager.set_uniforms(self.shader, 0)

        self.skybox.back.bind(1)
        GL.glUniform1i(self.locations['env_tex_back'], 1)
        self.skybox.front.bind(2)
        GL.glUniform1i(self.locations['env_tex_front'], 2)
        GL.glUniformMatrix4fv(self.locations['env_rotation'], 1, True, self.skybox.rotation)

        GL.glUniform3fv(self.locations['w_camera_position'], 1, camera.position)

        super().draw(projection, view, model, normal_matrix, camera)

    def height(self, x, z):
        return noise(vec3(
                        POSITION_SCALING_FACTOR * x,
                        POSITION_SCALING_FACTOR * z,
                        TIME_SCALING_FACTOR * self.current_time))
