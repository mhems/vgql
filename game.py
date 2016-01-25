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
        deps = ' (%s)' % ', '.join(str(d) for d in self.deps)
        info = '\n    - %s' % self.info if self.info is not None else ''
        return deps + info

    def __eq__(self, other):
        '''Compare self and other for equality'''
        if isinstance(other, dict):
            return (self.kind == other['kind'] and
                    self.info == other['how'])
        return (self.kind == other.kind and
                self.info == other.info and
                self.deps == other.deps)

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

    def __eq__(self, other):
        '''Compare self and other for equality'''
        if super().__eq__(other):
            if isinstance(other, dict):
                return self.name == other['name']
            return self.name == other.name
        return False

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

    def __init__(self, entries=None):
        '''Initializes query parser and internalizes dictlist'''
        self.parser = parsing.QueryParser()
        self.entries = entries if entries is not None else []

    @staticmethod
    def fromWorlds(worlds, assume_not_found=True):
        '''Construct and return database from list of worlds'''
        entries = []
        for world in worlds:
            for room in world.rooms:
                for c in room.collectibles:
                    entry = {'found' : not assume_not_found,
                             'world' : world.name,
                             'kind' : c.kind,
                             'room' : room.name}
                    entry['how'] = c.info if c.info is not None else ''
                    if isinstance(c, Item):
                        entry['name'] = c.name
                    entries.append(entry_)
        return Database(entries)

    @property
    def collected(self):
        '''Returns list of collected items'''
        return self.filter(lambda i: i['found'] == True)

    @property
    def uncollected(self):
        '''Returns list of uncollected items'''
        return self.filter(lambda i: i['found'] == False)

    @property
    def upgrades(self):
        '''Returns list of collected upgrades'''
        return self.filter(lambda item: item['found'] == True and
                           item['kind'] == 'Upgrade')

    @property
    def percent_complete(self):
        '''Return percent of collectibles acquired'''
        return len(self.collected) / len(self)

    def pickup(self, collectible, room, world):
        '''Update found status of corresponding database entry to True'''
        updated = False
        for idx, entry in enumerate(self.uncollected):
            if (collectible == entry and
                room == entry['room'] and
                world == entry['world']):

                updated = True
                self.entries[idx]['found'] = True
                break
        assert(updated)

    def sort(self, key=None, reverse=False):
        '''Sort items in-place by key and reverse flag'''
        self.entries.sort(key=key, reverse=reverse)

    def sorted(self, key=None, reverse=False):
        '''Return sorted copy of items by key and reverse flag'''
        return sorted(self.entries, key=key, reverse=reverse)

    def __len__(self):
        '''Return number of items in self'''
        return len(self.entries)

    def __str__(self):
        '''Return line-separated items in self'''
        return '\n'.join(str(i) for i in self.entries)

    def __repr__(self):
        ''''Return database in JSON-like notation'''
        core = '\n'.join(str(i) for i in self.entries)
        return '{\n\"itemlist\":[\n%s\n]\n}' % core

    def read(self, filename):
        '''Parse items in filename into database'''
        with open(filename, 'r') as f:
            self.entries = json.load(f)['itemlist']

    def write(self, filename):
        '''Write database to source'''
        with open(filename, 'w') as f:
            json.dump({'itemlist' : self.entries}, f, indent=2)

    def query(self, string, exclude_found, update):
        '''Query database for all items satisfying constraints'''
        func = self.parser.parse(string)
        if exclude_found:
            test = lambda x : func(x) and x['found'] == False
        else:
            test = func
        if update:
            for idx, e in enumerate(self.entries):
                if test(e):
                    self.entries[idx]['found'] = True
        return self.filter(test)

    def filter(self, func):
        '''Filter database for all items for which func returns True'''
        return [e for e in self.entries if func(e)]

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
