'''
Module representing in-game objects

* Collectible
  |- Expansion
  |- Item
* Room
* World
* Database
* Game
'''

import os
import json

import configuration as config
import parsing
import graph

class Collectible:
    '''
    Represents an in-game collectible.

    A collectible has a kind and possibly a description on collecting
    it and a list of dependencies
    '''

    def __init__(self, kind, info=None, deps=None):
        '''Internalizes parameters'''
        self.kind = kind
        self.info = info
        self.deps = [] if deps is None else deps

    @property
    def _extra(self):
        '''Returns formatted string of possibly-None variables'''
        info = '\n    - %s' % self.info if self.info is not None else ''
        deps = ' (%s)' % ', '.join(str(d) for d in self.deps) if len(self.deps) > 0 else ''
        return '%s%s' % (deps, info)

class Expansion(Collectible):
    '''
    Category of collectibles that appear many times,
    each without a specific name
    '''

    def __init__(self, kind, info=None, deps=None):
        '''Internalizes parameters'''
        super().__init__(kind, info, deps)

    def __str__(self):
        '''Return formatted string holding contents of self'''
        return '  * %s%s' % (self.kind, self._extra)

class Item(Collectible):
    '''
    Category of unique collectibles that appear once,
    each with a specific name
    '''

    def __init__(self, name, kind, info=None, deps=None):
        '''Internalizes parameters'''
        super().__init__(kind, info)
        self.name = name

    def __str__(self):
        '''Return formatted string holding contents of self'''
        return '  * %s: %s%s' % (self.kind, self.name, self._extra)

class Room:
    '''
    Represents an in-game Room that holds collectibles and has adjacencies
    '''

    def __init__(self, name, world=None, collectibles=None, adjacencies=None):
        '''Internalizes parameters'''
        self.name = name
        self.world = world
        self.collectibles = collectibles if collectibles is not None else []
        self.adjacencies  = adjacencies  if adjacencies  is not None else []

    @property
    def numCollectibles(self):
        '''Return number of collectibles within self'''
        return len(self.collectibles)

    @property
    def numAdjacencies(self):
        '''Return number of rooms adjacent to self'''
        return len(self.adjacencies)

    @property
    def elevator(self):
        '''
        Return True if self is a room with an adjacent room in another world
        '''
        return any(r[2] != self.world
                   for r in self.adjacencies if r[2] is not None)

    def addCollectible(self, collectible):
        '''Adds collectible to self'''
        self.collectibles.append(collectible)

    def addAdjacency(self, adjacency):
        '''Adds adjacency to self'''
        self.adjacencies.append(adjacency)

    def __eq__(self, other):
        '''Return True iff self is equal to other'''
        return self.name == other.name and self.world == other.world

    def __str__(self):
        '''Return formatted string holding contents of self'''
        c = ''
        if len(self.collectibles) > 0:
            c = '\n'.join(str(c) for c in self.collectibles) + '\n'
        return '> %s\n%s  | %s\n' % (self.name,
                                     c,
                                     ', '.join(str(a) for a in self.adjacencies))

class World:
    '''Represents an in-game world - a set of interconnected Rooms'''

    def __init__(self, name):
        '''Internalizes parameters'''
        self.name = name
        self.rooms = []

    @property
    def numRooms(self):
        '''Return number of Rooms in self'''
        return len(self.rooms)

    def addRoom(self, room):
        '''Adds room to self'''
        self.rooms.append(room)

    def __str__(self):
        '''Return formatted string holding contents of self'''
        return '*** %s ***\n\n%s\n' % (self.name,
                                       '\n'.join(str(r) for r in self.rooms))

    def __contains__(self, room):
        '''Return True iff room contained in world'''
        return room in self.rooms

    def __iter__(self):
        '''Maintains iteration over self'''
        self.rooms.__iter__()

class Database:
    '''Mechanism for storing and querying items'''

    def __init__(self, dictlist=None):
        '''Initializes query parser and internalizes dictlist'''
        self.parser = parsing.QueryParser(config.get('CHOICES'))
        if dictlist is not None:
            self.dicn = { 'itemlist' : dictlist }

    @staticmethod
    def fromWorlds(worlds, assume_not_found=True):
        '''Construct and return database from list of worlds'''
        dictlist = []
        for world in worlds:
            for room in world.rooms:
                for c in room.collectibles:
                    dict_ = {'found' : not assume_not_found,
                             'world' : world.name,
                             'kind' : c.kind,
                             'room' : room.name}
                    dict_['how'] = c.info if c.info is not None else ''
                    if isinstance(c, Item):
                        dict_['name'] = c.name
                    dictlist.append(dict_)
        return Database(dictlist)

    @property
    def items(self):
        '''Returns list of items, each a dict'''
        return self.dicn['itemlist']

    def sort(self, key=None, reverse=False):
        '''Sort items by key and reverse flag'''
        self.items.sort(key=key, reverse=reverse)

    def __len__(self):
        '''Return number of items in self'''
        return len(self.items)

    def __str__(self):
        '''Return line-separated items in self'''
        return '\n'.join(str(i) for i in self.items)

    def __repr__(self):
        ''''Return database in JSON-like notation'''
        core = '\n'.join(str(i) for i in self.items)
        return '{\n\"itemlist\":[\n%s\n]\n}' % core

    def read(self, filename):
        '''Parse items in filename into database'''
        with open(filename, 'r') as f:
            self.dicn = json.load(f)

    def write(self, filename):
        '''Write database to source'''
        with open(filename, 'w') as f:
            json.dump(self.dicn, f, indent=2)

    def query(self, string, exclude_found, update):
        '''Query database for all items satisfying constraints'''
        func = self.parser.parse(string)
        if exclude_found:
            test = lambda x : func(x) and x['found'] == False
        else:
            test = func
        if update:
            for idx, e in enumerate(self.items):
                if test(e):
                    self.dicn['itemlist'][idx]['found'] = True
        return [e for e in self.items if test(e)]

class Game:
    '''
    Top-level representation of a game's internals such as
    map, collectibles, and player progress
    '''

    def __init__(self, config_file):
        '''Load configuration and load game data as graph'''
        config.loadConfiguration(config_file)
        worlds = parsing.DataParser(config.get('GAME_DATA')).parse()

        self.graph = graph.Graph.fromWorlds(worlds)
        if not os.path.exists(config.get('DATABASE')):
            self.database = Database.fromWorlds(worlds)
            self.database.write(config.get('DATABASE'))
        else:
            self.database = Database()
            self.database.read(config.get('DATABASE'))
