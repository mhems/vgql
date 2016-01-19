'''
Module containing graph-related objects

* GraphEdge
* GraphNode
* Graph
'''

class GraphEdge:
    '''Simple class for an directed Graph Edge with at most one dependency'''

    def __init__(self, a, b, dep=None):
        self.a = a
        self.b = b
        self.dep = dep

class GraphNode:
    '''
    Simple wrapper container for an Object to be a node in a Graph.
    A Node holds its out-edges but knows nothing of its in-edges.
    '''

    def __init__(self, value, adjacencies=None):
        '''Internalizes parameters'''
        self.value = value
        self.adjacencies = [] if adjacencies is None else adjacencies

    @property
    def key(self):
        '''Returns the key of the node'''
        return self.value.name

    @property
    def degree(self):
        '''Returns the number of out-edges'''
        return len(self.adjacencies)

    @property
    def isLeaf(self):
        '''Returns True if self is a leaf node (only one out-edge)'''
        return self.degree == 1

class Graph:
    '''
    Directed adjacency-list graph where an edge is traversable if
    there is no dependency or the single dependency has been satisfied
    '''

    def __init__(self):
        '''Constructs self'''
        self.nodes = []
        self.map = {}

    def addNode(self, node):
        '''Adds node to internal structure'''
        self.nodes.append(node)
        self.map[node.key] = node

    def removeNode(self, node):
        '''Removes and returns node from internal structure'''
        self.nodes.remove(node)
        return self.map.pop[node.key]

    def __len__(self):
        '''Return number of nodes in self'''
        return len(self.nodes)

    def __contains__(self, node):
        '''Return True iff node is a node in self'''
        return node in self.nodes

    def __iter__(self):
        '''Maintains iteration over self'''
        self.nodes.__iter__()
