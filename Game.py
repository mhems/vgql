class GraphNode:

    def __init__(self, value, adjacencies):
        self.value = value
        self.adjacencies = adjacencies

class Graph:

    def __init__(self):
        self.nodes = []

    def addNode(self, node):
        self.nodes.append(node)

    def removeNode(self, node):
        self.nodes.remove(node)

    def __len__(self):
        return len(self.nodes)

class Collectible:

    def __init__(self, kind, info=None, deps=None):
        self.kind = kind
        self.info = info
        self.deps = deps if deps is not None else []

    @property
    def extra(self):
        info = '\n    - %s' % self.info if self.info is not None else ''
        deps = ' (%s)' % ', '.join(str(d) for d in self.deps) if len(self.deps) > 0 else ''
        return '%s%s' % (deps, info)

class Expansion(Collectible):

    def __init__(self, kind, info=None, deps=None):
        super().__init__(kind, info, deps)

    def __str__(self):
        return '  * %s%s' % (self.kind, self.extra)

class Item(Collectible):

    def __init__(self, name, kind, info=None, deps=None):
        super().__init__(kind, info)
        self.name = name

    def __str__(self):
        return '  * %s: %s%s' % (self.kind, self.name, self.extra)

class Room:

    def __init__(self, name, collectibles=None, adjacencies=None):
        self.name = name
        self.collectibles = collectibles if collectibles is not None else []
        self.adjacencies  = adjacencies  if adjacencies  is not None else []

    @property
    def numCollectibles(self):
        return len(self.collectibles)

    @property
    def numAdjacencies(self):
        return len(self.adjacencies)

    def addCollectible(self, collectible):
        self.collectibles.append(collectible)

    def addAdjacency(self, adjacency):
        self.adjacencies.append(adjacency)

    def __str__(self):
        c = ''
        if len(self.collectibles) > 0:
            c = '\n'.join(str(c) for c in self.collectibles) + '\n'
        return '> %s\n%s  | %s\n' % (self.name,
                                     c,
                                     ', '.join(str(a) for a in self.adjacencies))

class World:

    def __init__(self, name):
        self.name = name
        self.rooms = []

    @property
    def numRooms(self):
        return len(self.rooms)

    def addRoom(self, room):
        self.rooms.append(room)

    def __str__(self):
        return '*** %s ***\n\n%s\n' % (self.name,
                                       '\n'.join(str(r) for r in self.rooms))
