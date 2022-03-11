#!/usr/bin/env python3

import numpy as np

from core.transform import identity


class Node:
    """ Scene graph transform and parameter broadcast node """
    def __init__(self, children=(), transform=identity()):
        self.set_transform(transform)
        self.children = list(iter(children))

    def set_transform(self, transform):
        self.transform = transform
        self.normal_matrix = np.linalg.inv(self.transform).T

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        self.children.extend(drawables)

    def update(self, delta_time):
        """ Recursive update """
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(delta_time)

    def draw(self, projection, view, model, normal_matrix, camera):
        """ Recursive draw """
        for child in self.children:
            if hasattr(child, 'draw'):
                child.draw(projection, view, model @ self.transform, normal_matrix @ self.normal_matrix, camera)

    def key_handler(self, key, is_press):
        """ Dispatch keyboard events to children """
        for child in self.children:
            if hasattr(child, 'key_handler'):
                child.key_handler(key, is_press)
