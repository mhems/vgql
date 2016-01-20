#!/usr/bin/python3

import pydotplus as pydot
from sys import argv

from parsing import DataParser
from graph import (Graph, GraphNode)
import configuration as config

if __name__ == '__main__':
    config.loadConfiguration('metroid_prime/config.json')
    parser = DataParser(argv[1])
    worlds = parser.parse()
    # print('\n\n'.join(str(w) for w in worlds))

    world_color_map = config.get('WORLD_COLORS')
    door_color_map = config.get('DOOR_COLORS')
    map = {}

    def hash(world, room):
        return (room  if isinstance(room,  str) else room.name,
                world if isinstance(world, str) else world.name)

    g = Graph()
    graph = pydot.Dot(graph_type='digraph',
                      bgcolor=config.get('BACKGROUND'))
    nodes = []
    for world in worlds:
        for room in world.rooms:
            g.addNode(GraphNode(room, room.adjacencies))
            color = world_color_map[room.world]
            if room.elevator:
                color = world_color_map['Elevator']
            node = pydot.Node(str(hash(world, room)),
                              label=room.name,
                              style='filled',
                              fillcolor=color)
            map[hash(world, room)] = node
            nodes.append(node)
            graph.add_node(node)
    for world in worlds:
        for room in world.rooms:
            for adj in room.adjacencies:
                a = map[hash(world, room)]
                adj_world = world
                if adj[2] is not None:
                    adj_world = adj[2]
                b = map[hash(adj_world, adj[0])]
                color = door_color_map['default']
                if adj[1] is not None:
                    color = door_color_map[adj[1][0]]
                graph.add_edge(pydot.Edge(a, b, color=color))
    graph.write_png('map.png')
