#!/usr/bin/env python3

import numpy as np
import glfw

from core.transform import vec, lerp, sincos, lookat, perspective
from player import SHIP_MAX_SIZE


PITCH_DEFAULT, PITCH_MIN, PITCH_MAX = 20, -7, 41
YAW_SPEED = 4
DISTANCE_DEFAULT, DISTANCE_MIN, DISTANCE_MAX = 11, 2, 20
MOUSE_SENSITIVITY = 180
SCROLL_SENSITIVITY = 0.5
FIELD_OF_VIEW = 70
Z_NEAR, Z_FAR = 0.5, 256


class Camera:
    def __init__(self, player):
        self.player = player

        self.mouse_position = vec(0, 0)
        self.yaw = 180 - self.player.angle
        self.pitch = PITCH_DEFAULT
        self.distance = DISTANCE_DEFAULT

        self.position = vec(0, 0, 0)
        self.target = vec(0, 0, 1)
        self.up = vec(0, 1, 0)

        self.viewport = (0, 0)

    def update(self, delta_time):
        yaw_target = 180 - self.player.angle
        t = np.clip(YAW_SPEED * delta_time, 0, 1)
        self.yaw = lerp(self.yaw, yaw_target, t)

        self.target = self.player.position + self.player.local_center
        front, self.up = self._directions()
        self.position = self.target + self.distance * front

    def on_mouse_move(self, window, xpos, ypos):
        old_position = self.mouse_position
        self.mouse_position = vec(xpos, glfw.get_window_size(window)[1] - ypos)
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT):
            winsize = glfw.get_window_size(window)
            _, dy = (self.mouse_position - old_position) / winsize
            self.pitch -= MOUSE_SENSITIVITY * dy
            self.pitch = np.clip(self.pitch, PITCH_MIN, PITCH_MAX)

    def on_scroll(self, window, _deltax, deltay):
        self.distance -= SCROLL_SENSITIVITY * deltay
        self.distance = np.clip(self.distance, SHIP_MAX_SIZE / 2 + DISTANCE_MIN, DISTANCE_MAX)

    def view_matrix(self):
        return lookat(self.position, self.target, self.up)

    def projection_matrix(self, winsize):
        aspect = winsize[0] / winsize[1] if winsize[0] != 0 and winsize[1] != 0 else 1
        return perspective(FIELD_OF_VIEW, aspect, Z_NEAR, Z_FAR)

    def _directions(self):
        sin_yaw, cos_yaw = sincos(self.yaw)
        sin_pitch, cos_pitch = sincos(self.pitch)
        front = vec(cos_yaw * cos_pitch,
                    sin_pitch,
                    sin_yaw * cos_pitch)
        side = np.cross(vec(0, 1, 0), front)
        up = np.cross(front, side)
        return front, up
