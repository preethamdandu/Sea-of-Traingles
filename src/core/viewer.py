#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw

from core.node import Node
from core.transform import identity


class Viewer(Node):
    """ GLFW viewer window, with classic initialization & graphics loop """
    def __init__(self, width, height, title):
        super().__init__()

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, True)
        glfw.window_hint(glfw.SAMPLES, 4)

        self.title = title
        self.window = glfw.create_window(width, height, self.title, None, None)
        glfw.make_context_current(self.window)

        # default OpenGL state
        GL.glClearColor(0, 0, 0, 0)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glProvokingVertex(GL.GL_FIRST_VERTEX_CONVENTION)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glEnable(GL.GL_TEXTURE_CUBE_MAP_SEAMLESS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_MULTISAMPLE)

        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_window_size_callback(self.window, self.on_size)

        self.camera = None

    def set_camera(self, camera):
        self.camera = camera
        self.camera.viewport = glfw.get_framebuffer_size(self.window)
        glfw.set_cursor_pos_callback(self.window, self.camera.on_mouse_move)
        glfw.set_scroll_callback(self.window, self.camera.on_scroll)

    def run(self):
        """ Main render loop for this OpenGL window """
        if self.camera is None:
            print('Warning: Viewer.camera is None')
            return

        last_update = glfw.get_time()
        last_framerate_update = last_update
        nb_frames_per_second = 0
        while not glfw.window_should_close(self.window):
            # clear draw buffer and depth buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # update our scene
            current_time = glfw.get_time()
            delta_time = current_time - last_update
            self.update(delta_time)
            last_update = current_time

            # get view and projection matrix from camera
            size = glfw.get_window_size(self.window)
            view = self.camera.view_matrix()
            projection = self.camera.projection_matrix(size)

            # draw our scene
            self.draw(projection, view, identity(), identity(), self.camera)

            # flush and swap buffers
            glfw.swap_buffers(self.window)

            # update framerate information
            nb_frames_per_second += 1
            current_time = glfw.get_time()
            delta_time = current_time - last_framerate_update
            if delta_time >= 1:
                ms_per_frame = 1000 * delta_time / nb_frames_per_second
                glfw.set_window_title(self.window, '{} - {:.1f} ms'.format(self.title, ms_per_frame))
                last_framerate_update = current_time
                nb_frames_per_second = 0

            # Poll and process new events
            glfw.poll_events()

    def on_key(self, _window, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        is_press = action == glfw.PRESS or action == glfw.REPEAT
        if is_press and (key == glfw.KEY_ESCAPE or key == glfw.KEY_Q):
            glfw.set_window_should_close(self.window, True)

        if action != glfw.REPEAT:
            self.key_handler(key, is_press)

    def on_size(self, window, width, height):
        """ update viewport to new framebuffer size """
        viewport = glfw.get_framebuffer_size(window)
        GL.glViewport(0, 0, *viewport)
        self.camera.viewport = viewport
