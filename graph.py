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
        '''Adds adjacency to node'''
        self.adjacencies.append(adjacency)

    def reachable(self, database):
        '''Return reachable adjacent nodes given database'''
        return [a[0] for a in self.adjacencies
                if a[1] is None or all(dep in database for dep in a[1])]

class Graph:
    '''
    Directed adjacency-list unweighted graph where an edge is
    traversable if there is no dependency or the single dependency has
    been satisfied
    '''

    def __init__(self):
        '''Constructs self'''
        self.nodes = []
        # map[(worldname, roomname)] holds node representing that room
        self.map = {}
        # dict where distm[(id(u), id(v))] holds distance from u to v
        self.distm = None

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
                    if adj[1] is not None:
                        assert(len(adj[1]) == 1)
                        node.addAdjacency((to, adj[1][0]))
                    else:
                        node.addAdjacency((to, None))
        return g

    @property
    def numNodes(self):
        '''Return number of nodes in self'''
        return len(self.nodes)

    @property
    def numEdges(self):
        '''Return number of edges in self'''
        return sum(n.degree for n in self.nodes)

    @property
    def density(self):
        '''Return density of graph, as defined by |E|/(|V|(|V|-1))'''
        N = self.numNodes
        return self.numEdges/(N * (N - 1))

    @property
    def max_degree(self):
        '''Returns degree of node with maximum degree'''
        return max(n.degree for n in self.nodes)

    @property
    def min_degree(self):
        '''Returns degree of node with minimum degree'''
        return min(n.degree for n in self.nodes)

    @property
    def diameter(self):
        '''Returns the maximum eccentricity over all nodes'''
        return max((self.eccentricity(v) for v in self.nodes
                    if self.eccentricity(v) > 0),
                   default=-1)

    @property
    def radius(self):
        '''Returns the minimum eccentricity over all nodes'''
        return min((self.eccentricity(v) for v in self.nodes
                    if self.eccentricity(v) > 0),
                   default=-1)

    def eccentricity(self, s):
        '''Returns greatest distance from s over all other nodes'''
        return max((self.distm[(id(s), id(i))] for i in self.nodes
                    if (id(s), id(i)) in self.distm and s is not i),
                   default=-1)

    def addNode(self, node):
        '''Adds node to internal structure'''
        self.nodes.append(node)
        self.map[node.key] = node

    def removeNode(self, node):
        '''Removes and returns node from internal structure'''
        self.nodes.remove(node)
        return self.map.pop[node.key]

    def distance(self, u, v):
        '''Returns distance from u to v or -1 if unreachable'''
        if self.distm is None:
            raise RuntimeError('must call compute_distances before distance')
        return self.distm[(id(u), id(v))]

    def compute_distances(self, database):
        '''
        Re-compute all-pairs distances given upgrades

        Uses extension of breadth-first-search as outlined here:
        http://faculty.simpson.edu/lydia.sinapova/www/cmsc250/LN250_Weiss/L21-MinPath.htm#unweighted
        '''
        # distm[(id(u), id(v))] holds distance from u to v,
        #                             -1 iff unreachable,
        #                              0 iff i == j
        self.distm = {}

        def compute_distance(s):
            '''Compute distance from s to all nodes'''
            # same as above
            distm = {}
            # holds nodes to be visited
            queue = [s]
            distm[(id(s), id(s))] = 0
            while len(queue) > 0:
                v = queue.pop(0)
                for w in v.reachable(database):
                    if not (id(s), id(w)) in distm:
                        distm[(id(s), id(w))] = distm[(id(s), id(v))] + 1
                        queue.append(w)
            distm.pop((id(s), id(s)))
            return distm

        for node in self.nodes:
            self.distm.update(compute_distance(node))

    def depth_first_search(self, start, database):
        '''Conduct a depth first search of graph, starting at start node'''
        for node in self.nodes:
            node.color = 'white'
            node.pred = None
        yield from self._dfs_visit(start, database)

    def _dfs_visit(self, start, database):
        '''Visits start and recursively visits adjacencies in dfs manner'''
        start.color= 'grey'
        yield start
        found = []
        for c in start.value.collectibles:
            if database.canPickup(c):
                database.pickup(c)
                found.append(c)
        if len(found) > 0:
            print('\n'.join(str(f) for f in found))
        for node in start.reachable(database.upgrades):
            if node.color == 'white':
                node.pred = start
                yield from self._dfs_visit(node, database)
        start.color = 'black'

    def write_png(self, filename):
        '''Create a png of the graph and write it to file '''
        graph = pydot.Dot(graph_type='digraph',
                          bgcolor=config.get('BACKGROUND'))
        for node in self.nodes:
            graph.add_node(node.node)
        for node in self.nodes:
            for adj in node.adjacencies:
                color = config.get('DOOR_COLORS')['default']
                if adj[1] is not None and adj[1] in config.get('DOOR_COLORS'):
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
