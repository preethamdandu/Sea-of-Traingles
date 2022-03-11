#!/usr/bin/env python3

import numpy as np


def vec3(x, y, z):
    return np.asarray((x, y, z))

def vec4(x, y, z, w):
    return np.asarray((x, y, z, w))

def step(edge, x):
    edge = (-2 * (np.abs(edge) < 1e-6) + 1) * edge
    return (x >= edge).astype(float)

def floor(x):
    return np.floor(x + 1e-6)

def swizzle3(v, x, y, z):
    return np.asarray((v[x], v[y], v[z]))

def swizzle4(v, x, y, z, w):
    return np.asarray((v[x], v[y], v[z], v[w]))

# Simplex Noise
# from "Efficient computational noise in GLSL" by Ian McEwan et al.
# https://github.com/ashima/webgl-noise/blob/master/src/noise3D.glsl

def mod289(x):
    return x - floor(x * (1.0 / 289.0)) * 289.0

def permute(x):
    return mod289(((x * 34.0) + 1.0) * x)

def taylorInvSqrt(r):
    return 1.79284291400159 - 0.85373472095314 * r

def snoise(v):
    C_xxx = vec3(1.0 / 6.0, 1.0 / 6.0, 1.0 / 6.0)
    C_yyy = vec3(1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    D = vec4(0.0, 0.5, 1.0, 2.0)

    # First corner
    i = floor(v + np.dot(v, C_yyy))
    x0 = v - i + np.dot(i, C_xxx)

    # Other corners
    g = step(swizzle3(x0, 1, 2, 0), x0)
    l = 1.0 - g
    l_zxy = swizzle3(l, 2, 0, 1)
    i1 = np.minimum(g, l_zxy)
    i2 = np.maximum(g, l_zxy)

    x1 = x0 - i1 + C_xxx
    x2 = x0 - i2 + C_yyy
    x3 = x0 - swizzle3(D, 1, 1, 1)

    # Permutations
    i = mod289(i)
    p = permute(permute(permute(
        i[2] + vec4(0.0, i1[2], i2[2], 1.0))
        + i[1] + vec4(0.0, i1[1], i2[1], 1.0))
        + i[0] + vec4(0.0, i1[0], i2[0], 1.0))

    # Gradients: 7x7 points over a square, mapped onto an octahedron.
    # The ring size 17*17 = 189 is close to a multiple of 49 (49*6 = 294)
    n_ = 0.142857142857
    ns = n_ * swizzle3(D, 3, 1, 2) - swizzle3(D, 0, 2, 0)

    j = p - 49.0 * floor(p * ns[2] * ns[2])

    x_ = floor(j * ns[2])
    y_ = floor(j - 7.0 * x_)

    ns_yyyy = swizzle4(ns, 1, 1, 1, 1)
    x = x_ * ns[0] + ns_yyyy
    y = y_ * ns[0] + ns_yyyy
    h = 1.0 - np.abs(x) - np.abs(y)

    b0 = vec4(x[0], x[1], y[0], y[1])
    b1 = vec4(x[2], x[3], y[2], y[3])

    s0 = floor(b0) * 2.0 + 1.0
    s1 = floor(b1) * 2.0 + 1.0
    sh = -step(h, 0.0)

    a0 = swizzle4(b0, 0, 2, 1, 3) + swizzle4(s0, 0, 2, 1, 3) * swizzle4(sh, 0, 0, 1, 1)
    a1 = swizzle4(b1, 0, 2, 1, 3) + swizzle4(s1, 0, 2, 1, 3) * swizzle4(sh, 2, 2, 3, 3)

    p0 = vec3(a0[0], a0[1], h[0])
    p1 = vec3(a0[2], a0[3], h[1])
    p2 = vec3(a1[0], a1[1], h[2])
    p3 = vec3(a1[2], a1[3], h[3])

    # Normalise gradients
    norm = taylorInvSqrt(vec4(np.dot(p0, p0), np.dot(p1, p1), np.dot(p2, p2), np.dot(p3, p3)))
    p0 *= norm[0]
    p1 *= norm[1]
    p2 *= norm[2]
    p3 *= norm[3]

    # Mix final noise value
    m = np.maximum(0.6 - vec4(np.dot(x0, x0), np.dot(x1, x1), np.dot(x2, x2), np.dot(x3, x3)), 0.0)
    m = m * m

    return 42.0 * np.dot(m * m, vec4(np.dot(p0, x0), np.dot(p1, x1), np.dot(p2, x2), np.dot(p3, x3)))

# End of Simplex Noise

def noise(x):
    s = 0.0
    amplitude = 1.0
    frequency = 1.0
    for _ in range(4):
        s += amplitude * snoise(frequency * x)
        amplitude *= 0.5
        frequency *= 2.0

    return s / 1.875
