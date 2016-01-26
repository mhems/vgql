#!/usr/bin/python3

'''
Ad-hoc test for game module
'''

import game

if __name__ == '__main__':
    game = game.Game('metroid_prime/config.json')
    g = game.graph
    # g.write_png('map.png')
    all = ['Space Jump Boots',
           'X-Ray Visor',
           'Morph Ball',
           'Wavebuster',
           'Varia Suit',
           'Charge Beam',
           'Morph Ball Bomb',
           'Ice Beam',
           'Ice Spreader',
           'Plasma Beam',
           'Wave Beam',
           'Boost Ball',
           'Super Missile',
           'Thermal Visor',
           'Spider Ball',
           'Gravity Suit',
           'Flamethrower',
           'Grapple Beam',
           'Phazon Suit']
    g.compute_distances(all)
    # print('\n'.join('%d: %d' % (i, id(k)) for i, k in enumerate(g.nodes)))
    # print('\n'.join('%s: %s' % (k, v) for k, v in g.distm.items()))
    print(g.max_degree, g.min_degree, g.diameter, g.radius)
