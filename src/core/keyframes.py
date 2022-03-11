#!/usr/bin/env python3

# MIT License does not apply
# code from: http://morpheo.inrialpes.fr/~franco/3dgraphics/

from bisect import bisect_left

from core.transform import lerp, quaternion_slerp, translate, quaternion_matrix, scale
from core.node import Node


class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function """
    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):
            # convert to list of pairs
            time_value_pairs = time_value_pairs.items()

        keyframes = sorted(time_value_pairs)
        # pairs list -> 2 lists
        self.times, self.values = zip(*keyframes)
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # Ensure time is within bounds else return boundary keyframe
        if time <= self.times[0]: return self.values[0]
        if time >= self.times[-1]: return self.values[-1]

        # Search for closest index entry in self.times
        index = bisect_left(self.times, time)

        # Using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        t = (time - self.times[index - 1]) / (self.times[index] - self.times[index - 1])

        return self.interpolate(self.values[index - 1], self.values[index], t)


class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """
    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.translate_keyframes = KeyFrames(translate_keys)
        self.rotate_keyframes = KeyFrames(rotate_keys, quaternion_slerp)
        self.scale_keyframes = KeyFrames(scale_keys)

    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """
        translation = translate(self.translate_keyframes.value(time))
        rotation = quaternion_matrix(self.rotate_keyframes.value(time))
        scaling = scale(self.scale_keyframes.value(time))

        return translation @ rotation @ scaling


class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    def __init__(self, translate_keys, rotate_keys, scale_keys, period):
        super().__init__()
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)
        self.period = period
        self.time = 0

    def update(self, delta_time):
        """ When update requested, interpolate our node transform from keys """
        self.time = (self.time + delta_time) % self.period
        self.set_transform(self.keyframes.value(self.time))
        super().update(delta_time)
