#!/usr/bin/env python3

import OpenGL.GL as GL
import numpy as np
from PIL import Image


class Texture:
    def __init__(self, filename):
        self.glid = GL.glGenTextures(1)

        try:
            data = np.asarray(Image.open(filename).convert('RGBA'))
        except FileNotFoundError:
            print('Error: unable to load file \'{}\''.format(filename))

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.glid)

        width, height = data.shape[1], data.shape[0]
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, data)

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    def bind(self, texture_unit):
        GL.glActiveTexture(GL.GL_TEXTURE0 + texture_unit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.glid)

    def __del__(self):
        GL.glDeleteTextures(self.glid)


class Cubemap:
    def __init__(self, *filenames):
        self.glid = GL.glGenTextures(1)

        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.glid)
        images = {}
        for i, filename in enumerate(filenames):
            try:
                if filename in images:
                    data = images[filename]
                else:
                    data = np.asarray(Image.open(filename).convert('RGBA'))
                    images[filename] = data
            except FileNotFoundError:
                print('Error: unable to load file \'{}\''.format(filename))

            width, height = data.shape[1], data.shape[0]
            GL.glTexImage2D(GL.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL.GL_RGBA,
                            width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, data)

        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_WRAP_R, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_CUBE_MAP, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        GL.glGenerateMipmap(GL.GL_TEXTURE_CUBE_MAP)

    def bind(self, texture_unit):
        GL.glActiveTexture(GL.GL_TEXTURE0 + texture_unit)
        GL.glBindTexture(GL.GL_TEXTURE_CUBE_MAP, self.glid)

    def __del__(self):
        GL.glDeleteTextures(self.glid)
