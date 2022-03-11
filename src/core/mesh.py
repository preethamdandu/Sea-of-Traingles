#!/usr/bin/env python3

import OpenGL.GL as GL

from core.vertex_array import VertexArray


class Mesh:
    """ Mesh to refactor all previous classes """
    def __init__(self, shader, attributes, index=None):
        self.shader = shader
        names = ['view', 'projection', 'model']
        self.locations = {name: GL.glGetUniformLocation(shader.glid, name) for name in names}
        self.vertex_array = VertexArray(attributes, index)

    def add_locations(self, *names):
        locations = {name: GL.glGetUniformLocation(self.shader.glid, name) for name in names}
        self.locations.update(locations)

    def draw(self, projection, view, model, normal_matrix, camera):
        GL.glUseProgram(self.shader.glid)

        GL.glUniformMatrix4fv(self.locations['view'], 1, True, view)
        GL.glUniformMatrix4fv(self.locations['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(self.locations['model'], 1, True, model)

        self.vertex_array.execute(GL.GL_TRIANGLES)
