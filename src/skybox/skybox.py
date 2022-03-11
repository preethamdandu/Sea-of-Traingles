#!/usr/bin/env python3

import OpenGL.GL as GL

from core.shader import Shader
from core.mesh import Mesh
from core.texture import Cubemap
from core.transform import identity, rotate


VERTEX_SHADER_NAME = 'skybox/skybox.vert'
FRAGMENT_SHADER_NAME = 'skybox/skybox.frag'
TEXTURES_BACK_NAME = ('../assets/skybox/back/{}.png'.format(name)
                        for name in ('side', 'side', 'top', 'top', 'front', 'side'))
TEXTURES_FRONT_NAME = ('../assets/skybox/front/{}.png'.format(name)
                        for name in ('right', 'left', 'top', 'top', 'front', 'back'))
CLOUDS_ANGULAR_VELOCITY = 0.5


class Skybox(Mesh):
    def __init__(self):
        shader = Shader(VERTEX_SHADER_NAME, FRAGMENT_SHADER_NAME)

        position = [(1.0, -1.0, 1.0), (1.0, -1.0, -1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0),
                    (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (-1.0, -1.0, 1.0)]
        index = [2, 1, 0, 0, 3, 2,
                 4, 5, 7, 7, 5, 6,
                 2, 3, 5, 5, 3, 6,
                 0, 1, 4, 4, 7, 0,
                 0, 7, 3, 3, 7, 6,
                 1, 2, 4, 4, 2, 5]

        super().__init__(shader, (position,), index)

        self.add_locations('tex_back', 'tex_front')

        self.back = Cubemap(*TEXTURES_BACK_NAME)
        self.front = Cubemap(*TEXTURES_FRONT_NAME)

        self.angle = 0
        self.rotation = identity()

    def update(self, delta_time):
        self.angle += CLOUDS_ANGULAR_VELOCITY * delta_time
        self.rotation = rotate((0, 1, 0), -self.angle)

    def draw(self, projection, view, model, normal_matrix, camera):
        GL.glUseProgram(self.shader.glid)

        self.back.bind(0)
        GL.glUniform1i(self.locations['tex_back'], 0)
        self.front.bind(1)
        GL.glUniform1i(self.locations['tex_front'], 1)

        super().draw(projection, view, self.rotation, self.rotation, camera)
