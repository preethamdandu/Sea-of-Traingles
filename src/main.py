#!/usr/bin/env python3

import glfw

from core.viewer import Viewer
from parchment.parchment import Parchment
from lights_manager import LightsManager
from skybox.skybox import Skybox
from water.water import Water
from player import Player
from officer import Officer
from camera import Camera


def main():
    viewer = Viewer(960, 540, "Sea of Triangles")

    parchment = Parchment()
    viewer.add(parchment)

    lights_manager = LightsManager()
    lights_manager.set_directional_light((0, -0.5, -1), (0.75, 0.75, 0.75))
    parchment.add(lights_manager)

    skybox = Skybox()

    water = Water(lights_manager, skybox)
    parchment.add(water)

    parchment.add(skybox)

    player = Player(lights_manager, water)
    player.add(Officer(lights_manager))
    lights_manager.add(player)

    camera = Camera(player)
    viewer.set_camera(camera)
    viewer.add(camera)

    print("How to play:\n" +
            "\tup: move forward\n" +
            "\tleft / right: rotate\n" +
            "\tleft mouse button: rotate the camera up and down\n" +
            "\tscroll wheel: zoom in and out\n" +
            "\th: show / hide the help\n" +
            "\tescape: quit")

    viewer.run()

    # Remove circular references to avoid errors with glDelete*
    lights_manager.children = None


if __name__ == '__main__':
    glfw.init()
    main()
    glfw.terminate()
