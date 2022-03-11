#!/usr/bin/env python3

import OpenGL.GL as GL

from core.node import Node
from core.transform import vec, ortho, lookat, identity
from core.framebuffer import Framebuffer


NB_MAX_POINT_LIGHTS = 8
SHADOW_WIDTH, SHADOW_HEIGHT = 1024, 1024
SHADOW_PROJECTION = ortho(-4.5, 4.5, -4.5, 4.5, 48, 80)
SHADOW_DISTANCE = 64


class LightsManager(Node):
    def __init__(self):
        super().__init__()
        self.locations = {}
        self.point_lights = []
        self.directional_light = ((0, -1, 0), (0, 0, 0))
        self.shadow = Framebuffer(SHADOW_WIDTH, SHADOW_HEIGHT)
        self.shadow_viewproj = identity()

    def add_shader(self, shader):
        names = ['nb_point_lights']
        for i in range(NB_MAX_POINT_LIGHTS):
            names.append('point_lights[{}].position'.format(i))
            names.append('point_lights[{}].color_intensity'.format(i))

        names += ['directional_light.direction', 'directional_light.color_intensity',
                    'shadow_viewproj', 'shadow_map']

        self.locations[shader] = {name: GL.glGetUniformLocation(shader.glid, name) for name in names}

    def add_point_light(self, position, color_intensity):
        self.point_lights.append((position, color_intensity))

    def set_directional_light(self, direction, color_intensity):
        self.directional_light = (direction, color_intensity)

    def set_uniforms(self, shader, texture_unit):
        locations = self.locations[shader]

        GL.glUniform1i(locations['nb_point_lights'], len(self.point_lights))
        for i, point_light in enumerate(self.point_lights):
            position, color_intensity = point_light
            GL.glUniform3fv(locations['point_lights[{}].position'.format(i)], 1, position)
            GL.glUniform3fv(locations['point_lights[{}].color_intensity'.format(i)], 1, color_intensity)

        direction, color_intensity = self.directional_light
        GL.glUniform3fv(locations['directional_light.direction'], 1, direction)
        GL.glUniform3fv(locations['directional_light.color_intensity'], 1, color_intensity)

        GL.glUniformMatrix4fv(locations['shadow_viewproj'], 1, True, self.shadow_viewproj)
        GL.glActiveTexture(GL.GL_TEXTURE0 + texture_unit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.shadow.texture_glid)
        GL.glUniform1i(locations['shadow_map'], texture_unit)

    def draw(self, projection, view, model, normal_matrix, camera):
        GL.glViewport(0, 0, SHADOW_WIDTH, SHADOW_HEIGHT)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.shadow.glid)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)

        direction, _ = self.directional_light
        target = camera.player.position + camera.player.local_center
        light_position = target - SHADOW_DISTANCE * vec(direction)
        light_view = lookat(light_position, target, vec(0, 1, 0))
        self.shadow_viewproj = SHADOW_PROJECTION @ light_view

        super().draw(SHADOW_PROJECTION, light_view, model, normal_matrix, camera)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        # Render scene
        GL.glViewport(0, 0, *camera.viewport)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        super().draw(projection, view, model, normal_matrix, camera)
