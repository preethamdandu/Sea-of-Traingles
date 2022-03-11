#!/usr/bin/env python3

from core.transform import vec, quaternion, quaternion_from_axis_angle
from model.model import load_model
from core.keyframes import KeyFrameControlNode


OFFICER_NAME = '../assets/models/pirate_officer.obj'
OFFICER_PERIOD = 30
OFFICER_TRANSLATE = {0: vec(0, 23.15, 14),
                        4: vec(0, 23.15, 14),
                        5: vec(0, 23.15, 18),
                        7: vec(-8.7, 23.15, 18),
                        10: vec(-8.7, 23.15, 18),
                        11: vec(-8.7, 23.15, 14),
                        13: vec(-8.7, 12.75, 7.25),
                        18: vec(8.7, 12.75, 7.25),
                        20: vec(8.7, 23.15, 14),
                        21: vec(8.7, 23.15, 18),
                        23: vec(2.6, 23.15, 18),
                        24: vec(0, 23.15, 14)}
OFFICER_ROTATE = {0: quaternion(),
                    4: quaternion(),
                    5: quaternion_from_axis_angle((0, 1, 0), 90),
                    10: quaternion_from_axis_angle((0, 1, 0), 90),
                    11: quaternion(),
                    13: quaternion(),
                    14: quaternion_from_axis_angle((0, 1, 0), -90),
                    18: quaternion_from_axis_angle((0, 1, 0), -90),
                    19: quaternion_from_axis_angle((0, 1, 0), 180),
                    21: quaternion_from_axis_angle((0, 1, 0), 180),
                    22: quaternion_from_axis_angle((0, 1, 0), 90),
                    24: quaternion()}
OFFICER_SCALE = {0: 1}


class Officer(KeyFrameControlNode):
    def __init__(self, lights_manager):
        super().__init__(OFFICER_TRANSLATE, OFFICER_ROTATE, OFFICER_SCALE, OFFICER_PERIOD)

        officer = load_model(OFFICER_NAME, lights_manager)
        self.add(*officer)
