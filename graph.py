'''
Module containing graph-related objects

* GraphNode
* Graph
'''

import pydotplus as pydot

import configuration as config

class GraphNode:
    '''
    Simple wrapper container for an Object to be a node in a Graph.
    A Node holds its out-edges but knows nothing of its in-edges.
    '''

    def __init__(self, value, adjacencies=None):
        '''Internalizes parameters'''
        self.value = value
        self.adjacencies = [] if adjacencies is None else adjacencies
        color = config.get('WORLD_COLORS')[self.value.world]
        if self.value.elevator:
            color = config.get('WORLD_COLORS')['Elevator']
        self.node = pydot.Node(str((self.value.world, self.value.name)),
                               label=self.value.name,
                               style='filled',
                               fillcolor=color)

    @property
    def key(self):
        '''Returns the key of the node'''
        return (self.value.world, self.value.name)

    @property
    def degree(self):
        '''Returns the number of out-edges'''
        return len(self.adjacencies)

    @property
    def isLeaf(self):
        '''Returns True if self is a leaf node (only one out-edge)'''
        return self.degree == 1

    def addAdjacency(self, adjacency):
        self.adjacencies.append(adjacency)

class Graph:
    '''
    Directed adjacency-list graph where an edge is traversable if
    there is no dependency or the single dependency has been satisfied
    '''

    def __init__(self):
        '''Constructs self'''
        self.nodes = []
        self.map = {}

    @staticmethod
    def fromWorlds(worlds):
        '''Constructs a Graph from a list of World objects'''
        g = Graph()
        for world in worlds:
            for room in world.rooms:
                g.addNode(GraphNode(room))
        for world in worlds:
            for room in world.rooms:
                node = g.map[(world.name, room.name)]
                for adj in room.adjacencies:
                    worldname = world.name
                    if adj[2] is not None:
                        worldname = adj[2]
                    to = g.map[(worldname, adj[0])]
                    dep = None
                    if adj[1] is not None:
                        dep = adj[1][0]
                    node.addAdjacency((to, dep))
        return g

    def addNode(self, node):
        '''Adds node to internal structure'''
        self.nodes.append(node)
        self.map[node.key] = node

    def removeNode(self, node):
        '''Removes and returns node from internal structure'''
        self.nodes.remove(node)
        return self.map.pop[node.key]

    def write_png(self, filename):
        graph = pydot.Dot(graph_type='digraph',
                          bgcolor=config.get('BACKGROUND'))
        for node in self.nodes:
            graph.add_node(node.node)
        for node in self.nodes:
            for adj in node.adjacencies:
                color = config.get('DOOR_COLORS')['default']
                if adj[1] is not None:
                    color = config.get('DOOR_COLORS')[adj[1]]
                graph.add_edge(pydot.Edge(node.node, adj[0].node, color=color))
        graph.write_png(filename)

    def __len__(self):
        '''Return number of nodes in self'''
        return len(self.nodes)

    def __contains__(self, node):
        '''Return True iff node is a node in self'''
        return node in self.nodes

    def __iter__(self):
        '''Maintains iteration over self'''
        self.nodes.__iter__()
