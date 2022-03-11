#!/usr/bin/env python3

import numpy as np
import glfw

from core.node import Node
from core.transform import vec, sincos, scale, rotate, translate
from model.model import Model, load_model


SHIP_NAME = '../assets/models/ship_light.obj'
SHIP_MAX_SIZE = 8
SHIP_DEFAULT_ANGLE = -45
SHIP_SPEED = 4
SHIP_ANGULAR_VELOCITY = 75
HEIGHT_DEFAULT = -0.25
HEIGHT_WATER_SCALING = 0.25
HEIGHT_DIRECTION_BIAIS = -0.25
ROLL_SCALING = 0.5


class Player(Node):
    def __init__(self, lights_manager, water):
        super().__init__()

        self.water = water

        ship = load_model(SHIP_NAME, lights_manager)
        self.add(*ship)

        lowers, uppers = zip(*[child.bounds for child in ship])
        self.bounds = (np.min(lowers, axis=0), np.max(uppers, axis=0))
        self.scaling = SHIP_MAX_SIZE / np.max(self.bounds[1] - self.bounds[0])
        self.bounds = (self.bounds[0] * self.scaling, self.bounds[1] * self.scaling)
        self.diagonal = self.bounds[1] - self.bounds[0]
        self.local_center = sum(self.bounds) / 2

        self.position = vec(0, 0, 0)
        self.roll_time = 0
        self.speed = 0
        self.angle = SHIP_DEFAULT_ANGLE
        self.angular_velocity = [0, 0]

    def update(self, delta_time):
        self.angle += delta_time * sum(self.angular_velocity)
        rotation = translate(self.local_center) @ rotate((0, 1, 0), self.angle - 90) @ translate(-self.local_center)

        sin_angle, cos_angle = sincos(self.angle)
        direction = vec(cos_angle, 0, -sin_angle)

        self.position += delta_time * self.speed * direction

        x, _, z = self.position - (self.diagonal[2] / 2 + HEIGHT_DIRECTION_BIAIS) * direction
        height = HEIGHT_DEFAULT + HEIGHT_WATER_SCALING * self.water.height(x, z)

        translation = translate(self.position + vec(0, height, 0))

        rolling = rotate((0, 0, 1), ROLL_SCALING * periodic(self.roll_time))
        self.roll_time += delta_time

        self.set_transform(translation @ rotation @ rolling @ scale(self.scaling))

        super().update(delta_time)

    def key_handler(self, key, is_press):
        if key == glfw.KEY_UP:
            self.speed = SHIP_SPEED if is_press else 0
        elif key == glfw.KEY_LEFT:
            self.angular_velocity[0] = SHIP_ANGULAR_VELOCITY if is_press else 0
        elif key == glfw.KEY_RIGHT:
            self.angular_velocity[1] = -SHIP_ANGULAR_VELOCITY if is_press else 0

        super().key_handler(key, is_press)


def smoothstep(x):
    return x * x * (3 - 2 * x)


def periodic(x):
    x = x % 2
    y = smoothstep(x) if x < 1 else smoothstep(2 - x)
    return 2 * y - 1
