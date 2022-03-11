#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw

from core.node import Node
from core.shader import Shader
from core.mesh import Mesh
from core.texture import Texture


VERTEX_SHADER_NAME = 'parchment/parchment.vert'
FRAGMENT_SHADER_NAME = 'parchment/parchment.frag'
TEXTURE_NAME = '../assets/parchment.png'
SIZE = 0.75

class Parchment(Node):
    def __init__(self):
        super().__init__()

        shader = Shader(VERTEX_SHADER_NAME, FRAGMENT_SHADER_NAME)
        position = [(-SIZE, -SIZE), (SIZE, -SIZE), (SIZE, SIZE), (-SIZE, SIZE)]
        tex_coords = [(0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
        index = [0, 1, 2, 0, 2, 3]

        self.mesh = Mesh(shader, (position, tex_coords), index)
        self.mesh.add_locations('tex')

        self.texture = Texture(TEXTURE_NAME)

        self.hidden = False
        self.keystates = {}

    def draw(self, projection, view, model, normal_matrix, camera):
        super().draw(projection, view, model, normal_matrix, camera)

        if self.hidden:
            return

        GL.glUseProgram(self.mesh.shader.glid)

        self.texture.bind(0)
        GL.glUniform1i(self.mesh.locations['tex'], 0)

        self.mesh.draw(projection, view, model, normal_matrix, camera)

    def key_handler(self, key, is_press):
        self.keystates[key] = is_press

        if self.hidden:
            super().key_handler(key, is_press)

        if key == glfw.KEY_H and is_press:
            self.hidden = not self.hidden
            for key, is_press in self.keystates.items():
                super().key_handler(key, self.hidden and is_press)
