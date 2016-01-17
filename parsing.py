from collections import OrderedDict
from copy import deepcopy
from io import TextIOBase
from re import (finditer, match, I)
from sys import argv
from itertools import groupby

from Game import (World, Room, Expansion, Item)

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

    def __init__(self, contents, asFile, tokenAssocs):
        '''Internalize parameters and prepare for lexing'''
        self.contents = contents
        self.asFile = asFile
        self.keys = [k for k, _ in tokenAssocs]
        self.regex = '|'.join('(?P<%s>%s)' % (k, v)
                              for k, v in tokenAssocs if v)
        self.toks = []

    def lex(self):
        '''Return contents as Token stream'''
        if self.asFile:
            with open(self.contents, 'r') as fil:
                return self._lex_lines(fil.readlines())
        return self._lex_lines(self.contents.split('\n'))

    def _lex_lines(self, lines):
        '''Helper method to lex lines of strings into Token stream'''
        for lineno, line in enumerate(lines):
            for match in finditer(self.regex, line.rstrip()):
                if match is not None:
                    for key in self.keys:
                        lexeme = match.group(key)
                        if ( lexeme is not None and
                             lexeme.strip() != '' ):
                            self.toks.append(Token(key,
                                                   lexeme.strip(),
                                                   lineno + 1,
                                                   match.start()))
                            break
        self.toks.append(Token('EOF', '__EOF__', lineno + 1, 0))
        return self._coalesce()

    def _coalesce(self):
        '''Join adjacent STRING tokens'''
        toks = []
        for key, groups in groupby(self.toks,
                                   lambda x: x.kind):
            l = list(groups)
            toks.append(Token(key,
                              ' '.join(g.lexeme for g in l),
                              l[0].lineno,
                              l[0].colno))
        self.toks = toks
        return self.toks

    def __str__(self):
        '''Return line separated token stream for debugging purposes'''
        return '\n'.join(str(t) for t in self.toks)

class Parser:
    '''
    Parser base class with utility methods for subclasses to use

    Subclasses should define a list of pair associations to pass to
    the Lexer constructor. This is a list of tuples that associate a
    Token kind to Token lexeme regular expression. A list is used
    instead of a (ordered) dictionary so that that declaration order
    may be honored.
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
        return self.index == len(self.tokenStream) - 1

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
                'Expected token to be one of %s, received kind %s (%s)'
                % (list(kinds),
                   self.lookahead.kind,
                   self.lookahead.lexeme))

class QueryParser(Parser):
    '''
    Simple parser of SQL-like query strings

    Parses the following grammar and synthesizes a filter function
    that will filter out all non-matching items of query

    start:  expr ? ;
    expr:   expr OR term
        |   term ;
    term:   term AND factor
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

    tokenAssocs = [
        ('AND', 'and|\\&'),
        ('OR', 'or|\\|'),
        ('TEST', '(\\!|\\=)\\='),
        ('LP', '\\('),
        ('RP', '\\)'),
        ('STRING', '[a-zA-z*]+')
    ]

    def __init__(self, choices, query):
        '''Lexes query and prepares for parsing'''
        copy = deepcopy(QueryParser.tokenAssocs)
        copy.insert(0, ('CHOICE', '|'.join(choices)))
        super().__init__(Lexer(query, False, copy).lex())

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
            return QueryParser._merge(t, e[0], e[1])
        return t

    def parse_EXPR_PRIME(self):
        if self.lookahead.kind == 'OR':
            self.match('OR')
            t = self.parse_TERM()
            e = self.parse_EXPR_PRIME()
            if e is not None:
                return ('or', QueryParser._merge(t, e[0], e[1]))
            return ('or', t)
        return None

    def parse_TERM(self):
        f = self.parse_FACTOR()
        t = self.parse_TERM_PRIME()
        if t is not None:
            return QueryParser._merge(f, t[0], t[1])
        return f

    def parse_TERM_PRIME(self):
        if self.lookahead.kind == 'AND':
            self.match('AND')
            f = self.parse_FACTOR()
            t = self.parse_TERM_PRIME()
            if t is not None:
                return ('and', QueryParser._merge(f, t[0], t[1]))
            return ('and', f)
        return None

    def parse_FACTOR(self):
        if self.lookahead.kind =='LP':
            self.match('LP')
            r = self.parse_EXPR()
            self.match('RP')
            return r
        c = self.match('CHOICE')
        t = self.match('TEST')
        s = self.match('STRING')
        func = (lambda item:
            match(s, str(item[c]), I) is not None)
        if t == '!=':
            return lambda x: not func(x)
        return func

    @staticmethod
    def _merge(f1, op, f2):
        if f2 is not None:
            if op == 'and':
                return lambda x: f1(x) and f2(x)
            elif op == 'or':
                return lambda x: f1(x) or f2(x)
            raise TypeError('unknown op: %s' % op)
        return f1

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

    tokenAssocs = [
        ('WB' , '\\*\\*\\*'),
        ('BULLET', '\\*'),
        ('BG' , '\\>'),
        ('COMMA' , '\\,'),
        ('PIPE' , '\\|'),
        ('COLON' , '\\:'),
        ('LP', '\\('),
        ('RP', '\\)'),
        ('INFO', '^\W*-\W*.*\W*$'),
        ('ID' , '[a-zA-Z0-9][-a-zA-Z0-9\'_ ]*')
    ]

    def __init__(self, filename):
        '''Lexes filename contents and prepares for parsing'''
        super().__init__(Lexer(filename, True, DataParser.tokenAssocs).lex())

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
