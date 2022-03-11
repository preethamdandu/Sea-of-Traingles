#!/usr/bin/env python3

import OpenGL.GL as GL
import numpy as np
import assimpcy

from core.shader import Shader
from core.mesh import Mesh


VERTEX_SHADER_NAME = 'model/model.vert'
FRAGMENT_SHADER_NAME = 'model/model.frag'


class Model(Mesh):
    def __init__(self, lights_manager, attributes, index=None,
                    k_a=(0, 0, 0), k_d=(1, 0, 0), k_s=(1, 1, 1), s=16.0):
        self.lights_manager = lights_manager

        shader = Shader(VERTEX_SHADER_NAME, FRAGMENT_SHADER_NAME)
        self.lights_manager.add_shader(shader)

        super().__init__(shader, attributes, index)

        self.k_a = k_a
        self.k_d = k_d
        self.k_s = k_s
        self.s = s

        self.add_locations('normal_matrix', 'k_a', 'k_d', 'k_s', 's', 'w_camera_position')

        position = attributes[0]
        self.bounds = (np.min(position, axis=0), np.max(position, axis=0))

    def draw(self, projection, view, model, normal_matrix, camera):
        GL.glUseProgram(self.shader.glid)

        self.lights_manager.set_uniforms(self.shader, 0)

        GL.glUniformMatrix4fv(self.locations['normal_matrix'], 1, True, normal_matrix)

        GL.glUniform3fv(self.locations['k_a'], 1, self.k_a)
        GL.glUniform3fv(self.locations['k_d'], 1, self.k_d)
        GL.glUniform3fv(self.locations['k_s'], 1, self.k_s)
        GL.glUniform1f(self.locations['s'], self.s)

        GL.glUniform3fv(self.locations['w_camera_position'], 1, camera.position)

        super().draw(projection, view, model, normal_matrix, camera)


def load_model(file, lights_manager, isSRGB=True):
    """ load resources from file using assimp, return list of Model """
    toLinearRGB = lambda color: np.power(color, 2.2) if isSRGB else color

    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_Triangulate | pp.aiProcess_GenSmoothNormals
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('Error: loading \'{}\': {}'.format(file, exception.args[0].decode()))
        return []

    # prepare model nodes
    models = []
    for mesh in scene.mMeshes:
        mat = scene.mMaterials[mesh.mMaterialIndex].properties
        model = Model(lights_manager, [mesh.mVertices, mesh.mNormals], mesh.mFaces,
                        k_a=toLinearRGB(mat.get('COLOR_AMBIENT', (0, 0, 0))),
                        k_d=toLinearRGB(mat.get('COLOR_DIFFUSE', (1, 0, 0))),
                        k_s=toLinearRGB(mat.get('COLOR_SPECULAR', (0.5, 0.5, 0.5))),
                        s=mat.get('SHININESS', 16.))
        models.append(model)

    return models
