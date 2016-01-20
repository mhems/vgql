#!/usr/bin/python3

import game

if __name__ == '__main__':
    game = game.Game('metroid_prime/config.json')
    game.graph.write_png('map.png')
