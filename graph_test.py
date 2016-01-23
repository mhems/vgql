#!/usr/bin/env python3

'''
Ad-hoc test for graph module
'''

import graph
import configuration as config

class NodeStub:
    '''Mock a Room object with an integer'''

    def __init__(self, value):
        '''Internalize value'''
        self.value = value

    @property
    def name(self):
        '''Return name of room'''
        return str(self.value)

    @property
    def world(self):
        '''Return the default'''
        return 'default'

    @property
    def elevator(self):
        '''No NodeStubs are elevators'''
        return False

if __name__ == '__main__':
    config.loadConfiguration('stub_config.json')
    g = graph.Graph()
    nodes = [graph.GraphNode(NodeStub(i)) for i in range(5)]
    deps = [None, None, 'Power', 'Turbo']
    for i, j in zip(range(4), deps):
        nodes[i].addAdjacency((nodes[i+1], j))
    for n in nodes:
        g.addNode(n)
    g.write_png('test.png')
    # print('\n'.join('%d: %d' % (i, id(k)) for i, k in enumerate(nodes)))
    g.compute_distances([])
    # print('\n'.join('%s: %s' % (k, v) for k, v in g.distm.items()))
    print(g.max_degree, g.min_degree, g.diameter, g.radius)
