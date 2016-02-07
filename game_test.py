#!/usr/bin/python3

'''
Ad-hoc test for game module
'''

import game

if __name__ == '__main__':
    game = game.Game('metroid_prime/config.json')
    # g = game.graph
    # g.write_png('map.png')

    # g.compute_distances(game.database)

    # print('\n'.join('%d: %d' % (i, id(k)) for i, k in enumerate(g.nodes)))
    # print('\n'.join('%s: %s' % (k, v) for k, v in g.distm.items()))

    # print(g.max_degree, g.min_degree, g.diameter, g.radius)
    # list(g.depth_first_search(game.start, game.database))
