#!/usr/bin/python3

from collections import OrderedDict
import re
import sys

from Game import *

# GRAMMAR

# start:      world + ;
# world:      WB ID WB room + ;
# room:       BG ID pickup * adj ? ;
# pickup:     BULLET ID (COLON ID) ? dep ? how ? ;
# how:        DASH INFO ;
# adj:        PIPE connection ( COMMA connection ) * ;
# connection: ID dep ?
# dep:        LP ID ( COMMA ID ) * RP ;

tokenMap = {
    'INFO': '^\W*-\W*.*\W*$',
    'ID' : '[a-zA-Z0-9][-a-zA-Z0-9\'_ ]*',
    'BULLET': '\\*',
    'BG' : '\\>',
    'WB' : '\\*\\*\\*',
    'COMMA' : '\\,',
    'PIPE' : '\\|',
    'COLON' : '\\:',
    'LP': '\\(',
    'RP': '\\)'
}

class Token:

    def __init__(self, kind, lexeme, lineno, colno):
        self.kind   = kind
        self.lexeme = lexeme
        self.lineno = lineno
        self.colno  = colno

    def __str__(self):
        return '(%s) "%s" @ (%d, %d)' % (self.kind,
                                         self.lexeme,
                                         self.lineno,
                                         self.colno)

    def error(self, msg=''):
        output = 'error at (%d, %d)' % (self.lineno, self.colno)
        if msg is not None:
            output += ': ' + msg
        print(output)

class Lexer:

    def __init__(self, filename, tokenMap):
        self.filename = filename
        # sort on length of regex to honor max-munch property
        self.tokenMap = OrderedDict(sorted(tokenMap.items(),
                                           key = lambda item : len(item[1]),
                                           reverse=True))
        # construct alternating named-group re from dict
        self.regex = '|'.join('(?P<%s>%s)' % (k, v) for k, v in self.tokenMap.items())
        self.toks = ''

    def lex(self):
        # return dict of token kind to token lexeme
        keys = list(self.tokenMap.keys())
        toks = []
        with open(self.filename, 'r') as fil:
            for lineno, line in enumerate(fil.readlines()):
                for match in re.finditer(self.regex, line.rstrip()):
                    if match is not None:
                        for key in keys:
                            lexeme = match.group(key)
                            if ( lexeme is not None and
                                 lexeme.strip() != '' ):
                                toks.append(Token(key,
                                                  lexeme.strip(),
                                                  lineno + 1,
                                                  match.start()))
                                break
        self.toks = toks
        return toks

    def __str__(self):
        return '\n'.join(str(t) for t in self.toks)

class Parser:

    EOF = '__EOF__'

    def __init__(self, tokenStream):
        self.tokenStream = tokenStream
        self.tokenStream.append( Token(Parser.EOF, '', 0, 0) )
        self.index = 0
        self.length = len(self.tokenStream)

    @property
    def lookahead(self):
        return self.tokenStream[self.index]

    def advance(self):
        if self.lookahead.kind != Parser.EOF:
            self.index += 1

    def match(self, *kinds):
        if self.lookahead.kind in kinds:
            tok = self.lookahead
            self.advance()
            return tok.lexeme
        else:
            self.lookahead.error(
                'Expected token of kind %s, received kind %s (%s)'
                % (kinds,
                   self.lookahead.kind,
                   self.lookahead.lexeme))

    def parse(self):
        worlds = []
        world = self.parse_world()
        while world is not None:
            worlds.append(world)
            world = self.parse_world()
        return worlds

    def parse_world(self):
        if self.lookahead.kind == 'WB':
            self.match('WB')
            worldname = self.match('ID')
            self.match('WB')
            world = World(worldname)
            room = self.parse_room(worldname)
            while room is not None:
                world.addRoom(room)
                room = self.parse_room(worldname)
            return world
        return None

    def parse_room(self, worldname):
        if self.lookahead.kind == 'BG':
            self.match('BG')
            roomname = self.match('ID')
            pickups = []
            pickup = self.parse_pickup()
            while pickup is not None:
                pickups.append(pickup)
                pickup = self.parse_pickup()
            adj = self.parse_adjacency()
            return Room(roomname, worldname, pickups, adj)
        return None


    def parse_pickup(self):
        if self.lookahead.kind == 'BULLET':
            self.match('BULLET')
            first = self.match('ID')
            second = None
            if self.lookahead.kind == 'COLON':
                self.match('COLON')
                second = self.match('ID')
            dep = self.parse_dependency()
            how = self.parse_how()
            if second is not None:
                return Item(second, first, how, dep)
            else:
                return Expansion(first, how, dep)
        return None

    def parse_how(self):
        if self.lookahead.kind == 'INFO':
            return re.match('^\W*-\W*(.*)\W*$', self.match('INFO')).group(1)
        return None

    def parse_adjacency(self):
        if self.lookahead.kind == 'PIPE':
            self.match('PIPE')
            connections = []
            connection = self.parse_connection()
            while connection is not None:
                connections.append(connection)
                if self.lookahead.kind == 'COMMA':
                    self.match('COMMA')
                connection = self.parse_connection()
            return connections
        return None

    def parse_connection(self):
        if self.lookahead.kind == 'ID':
            room = self.match('ID')
            dep = None
            if self.lookahead.kind == 'LP':
                dep = self.parse_dependency()
            return (room, dep)
        return None

    def parse_dependency(self):
        if self.lookahead.kind == 'LP':
            self.match('LP')
            deps = [self.match('ID')]
            while self.lookahead.kind == 'COMMA':
                self.match('COMMA')
                deps.append(self.match('ID'))
            self.match('RP')
            return deps
        return None

if __name__ == '__main__':
    lexer  = Lexer(sys.argv[1], tokenMap)
    tokStream = lexer.lex()
    # print('\n'.join(str(t) for t in tokStream))
    parser = Parser(tokStream)
    worlds = parser.parse()
    # print('\n\n'.join(str(w) for w in worlds))
    import pydotplus as pydot
    map = {}

    def hash(world, room):
        return (room  if isinstance(room,  str) else room.name,
                world if isinstance(world, str) else world.name)

    g = Graph()
    graph = pydot.Dot(graph_type='digraph', bgcolor='black')
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
                if room.elevator and Room.isElevator(adj[0]):
                    list = room.name.split()[2:]
                    if list[-1] in ['North', 'East', 'South', 'West']:
                        list = list[:-1]
                    adj_world = ' '.join(list)
                b = map[hash(adj_world, adj[0])]
                color = door_color_map['default']
                if adj[1] is not None:
                    color = door_color_map[adj[1][0]]
                graph.add_edge(pydot.Edge(a, b, color=color))
    graph.write_png('map.png')
