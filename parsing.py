from collections import OrderedDict
from io import TextIOBase
from re import (finditer, match, I)
from sys import argv

class Token:
    '''Simple struct of token data'''

    def __init__(self, kind, lexeme, lineno, colno):
        '''Assign parameters to member variables'''
        self.kind   = kind
        self.lexeme = lexeme
        self.lineno = lineno
        self.colno  = colno

    def __str__(self):
        '''Return formatted string representation of self'''
        return '(%s) "%s" @ (%d, %d)' % (self.kind,
                                         self.lexeme,
                                         self.lineno,
                                         self.colno)

    def error(self, msg):
        '''Print msg to stdout, prefixed by token information'''
        print('error at (%d, %d): %s' % (self.lineno, self.colno, msg))

class Lexer:
    '''
    Generic Lexer for lexing specified tokens from a filename into a
    stream of Tokens
    '''

    def __init__(self, contents, tokenMap):
        '''Internalize parameters and prepare for lexing'''
        self.contents = contents
        # sort on descending length of regex to achieve max-munch property
        self.tokenMap = OrderedDict(sorted(tokenMap.items(),
                                           key = lambda item : len(item[1]),
                                           reverse=True))
        self.regex = '|'.join('(?P<%s>%s)' % (k, v)
                              for k, v in self.tokenMap.items())
        self.toks = []

    def lex(self):
        '''Return contents as Token stream'''
        if isinstance(self.contents, TextIOBase):
            with open(self.contents, 'r') as fil:
                return self._lex_lines(fil.readlines())
        elif isinstance(self.contents, str):
            return self._lex_lines(self.contents.split('\n'))
        raise TypeError('invalid lexing contents')

    def _lex_lines(self, lines):
        '''Helper method to lex lines of strings into Token stream'''
        keys = list(self.tokenMap.keys())
        for lineno, line in enumerate(lines):
            for match in finditer(self.regex, line.rstrip()):
                if match is not None:
                    for key in keys:
                        lexeme = match.group(key)
                        if ( lexeme is not None and
                             lexeme.strip() != '' ):
                            self.toks.append(Token(key,
                                                   lexeme.strip(),
                                                   lineno + 1,
                                                   match.start()))
                            break
        return self.toks

    def __str__(self):
        '''Return line separated token stream for debugging purposes'''
        return '\n'.join(str(t) for t in self.toks)

class Parser:
    '''
    Parser base class with utility methods for subclasses to use
    '''

    def __init__(self, tokenStream):
        '''Internalize parameters and prepare for parsing'''
        self.tokenStream = tokenStream
        self.index = 0

    @property
    def lookahead(self):
        '''Return token currently being considered'''
        return self.tokenStream[self.index]

    @property
    def isExhausted(self):
        '''Return True iff token stream is exhausted'''
        return self.index == len(self.tokenStream)

    def advance(self):
        '''Advances parser to next token in stream unless at EOF'''
        if not self.isExhausted:
            self.index += 1

    def match(self, *kinds):
        '''
        Attempts to match lookahead to *kinds
        If successful, advances parser and returns the matching token
        On failure, issues an error on token with generic message
        '''
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

class QueryParser(Parser):
    '''
    Simple parser of SQL-like query strings

    Parses the following grammar and synthesizes a filter function
    that will filter out all non-matching items of query

    start:  expr ? ;
    expr:   expr AND term
        |   term ;
    term:   term OR factor
        |   factor ;
    factor: LP expr RP
          | CHOICE TEST STRING ;

    AND:    '&' | 'and' ;
    OR:     '|' | 'or' ;
    TEST:   '!=' | '==' ;
    LP:     '(' ;
    RP:     ')' ;
    STRING: /[a-zA-z *]+/ ;
    CHOICE: <GIVEN BY CONFIGURATION> ;
    '''

    tokenMap = {
        'AND': 'and|\\&' ,
        'OR': 'or|\\|' ,
        'TEST': '(\\!|\\=)\\=' ,
        'LP': '\\(',
        'RP': '\\)',
        'STRING': '[a-zA-z *]+'
    }

    def __init__(self, choices, query):
        '''Lexes filename contents and prepares for parsing'''
        self.choices = choices
        super().__init__(Lexer(query, QueryParser.tokenMap).lex())

    def parse(self):
        '''Synthesizes filter function from parsing query string'''
        return self.parse_START()

    def parse_START(self):
        if self.isExhausted:
            return lambda _ : True
        return self.parse_EXPR()

    def parse_EXPR(self):
        t = self.parse_TERM()
        e = self.parse_EXPR_PRIME()
        if e is not None:
            return _merge(t, e[0], e[1])
        return t

    def parse_EXPR_PRIME(self):
        if self.lookahead.kind == 'AND':
            self.match('AND')
            t = self.parse_TERM()
            e = self.parse_EXPR_PRIME()
            if e is not None:
                return ('and', _merge(t, e[0], e[1]))
            return ('and', t)
        return None

    def parse_TERM(self):
        f = self.parse_FACTOR()
        t = self.parse_TERM_PRIME()
        if t is not None:
            return _merge(f, t[0], t[1])
        return f

    def parse_TERM_PRIME(self):
        if self.lookahead.kind == 'OR':
            self.match('OR')
            f = self.parse_FACTOR()
            t = self.parse_TERM_PRIME()
            if t is not None:
                return ('or', _merge(f, t[0], t[1]))
            return ('or', f)
        return None

    def parse_FACTOR(self):
        if self.lookahead.kind =='LP':
            self.match('LP')
            r = parse_EXPR()
            self.match('RP')
            return r
        c = self.match('CHOICE')
        t = self.match('TEST')
        s = self.match('STRING')
        func = (lambda item:
            match(s, str(item[c]), I) is not None)
        if t == '!=':
            func = lambda x: not func(x)
        return func

    @staticmethod
    def _merge(self, f1, op=None, f2=None):
        if op is not None and f2 is not None:
            return {
                'and': lambda x: f1(x) and f2(x),
                'or':  lambda x: f1(x) or  f2(x)
            }[op]
        return f1

import Game

class DataParser(Parser):
    '''
    Simple parser of custom data format language

    Parses the following grammar synthesizes a list of World objects

    start:      world + ;
    world:      WB ID WB room + ;
    room:       BG ID pickup * adj ? ;
    pickup:     BULLET ID (COLON ID) ? dep ? how ? ;
    how:        DASH INFO ;
    adj:        PIPE connection ( COMMA connection ) * ;
    connection: ID dep ?
    dep:        LP ID ( COMMA ID ) * RP ;

    INFO:   /^\W*-\W*.*\W*$/ ;
    ID:     /[a-zA-Z0-9][-a-zA-Z0-9\_ ]*/ ;
    BULLET: '*' ;
    BG:     '>' ;
    WB:     '***' ;
    COMMA:  ',' ;
    PIPE:   '|' ;
    COLON:  ':' ;
    LP:     '(' ;
    RP:     ')' ;
    '''

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

    def __init__(self, choices):
        pass

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
            return match('^\W*-\W*(.*)\W*$', self.match('INFO')).group(1)
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
