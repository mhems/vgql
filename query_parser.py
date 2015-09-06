#!/usr/bin/python3

# Parsing functionality for basic SQL-like query languagle of form:
# select items where A == string1 and
#                    B == string2 or
#                    C != string3

# Grammar:
# START: EXPR ? ;
# EXPR: EXPR ( AND TERM )
#     | TERM
#     ;
# TERM: TERM OR FACTOR
#     | FACTOR
#     ;
# FACTOR: '(' EXPR ')'
#       | TEST
#       ;
# TEST: CHOICE '!'? '=' STRING ;
# AND: '&' | 'and' ;
# OR: '|' | 'or' ;
# CHOICE: 'kind' | 'room' | 'world' | 'name' ;
# STRING : [a-zA-z *]+ ;

# Refactored to remove direct left recursion
# START: EXPR ?;
# EXPR: TERM EXPR' ;
# EXPR': AND TERM EXPR'
#      | empty
#      ;
# TERM: FACTOR TERM' ;
# TERM': OR FACTOR TERM'
#      | empty
#      ;
# FACTOR: '(' EXPR ')'
#       | TEST
#       ;
# TEST: CHOICE '!'? '=' STRING ;
# AND: '&' | 'and' ;
# OR:  '|' | 'or'  ;
# CHOICE : 'kind' | 'room' | 'world' | 'name' ;
# STRING : [a-zA-z *]+ ;

import sys, re, itertools

# Synthesized attribute grammar that returns filter function to apply to dictionary

AND_OPTIONS = ['and', '&']
OR_OPTIONS  = ['or', '|']
SYMBOLS = ['==', '!=', '(', ')', '&', '|']
choices   = {}
stream    = None
lookahead = None

def advance():
    global stream, lookahead
    lookahead = stream.pop(0)

def parse(string):
    initialize(string)
    return parse_START()
    
def initialize(string):
    global stream, choices
    choices = {
        'Kind': 0,
        'Room': 0,
        'World': 0,
        'Name': 0
    }
    stream = lex(string)
    print(stream)
    stream.append('')
    advance()

def lex(string):
    # Yes, this is very poor code
    if string is not None and len(string) > 0:
        changing = True
        divs = set(itertools.chain(AND_OPTIONS, OR_OPTIONS, SYMBOLS))
        words = string.split()
        while changing:
            tokens = []
            changing = False
            for w in words:
                added = False
                for s in SYMBOLS:
                    if added:
                        break
                    if s in w and s != w:
                        (h, s, t) = w.partition(s)
                        if len(h) > 0:
                            tokens.append(h)
                        tokens.append(s)
                        if len(t) > 0:
                            tokens.append(t)
                        added = True
                        changing = True
                if not added:
                    tokens.append(w)
            words = tokens
        tokens = words
        # merge any adjacent words
        r = []
        i = 0
        end = len(tokens)
        while i < end:
            acc = tokens[i]
            while ( i < end - 1 and
                    tokens[i]   not in divs and
                    tokens[i+1] not in divs ) :
                acc += ' ' + tokens[i+1]
                tokens.pop(i+1)
                end -= 1
            r.append(acc)
            i += 1
        return r
    else:
        return []
    
def parse_START():
    if lookahead == '':
        return lambda _ : True
    else:
        return parse_EXPR()

def parse_EXPR():
    t = parse_TERM()
    e = parse_EXPR_PRIME()
    if e is not None:
        return merge_prime(t, e)
    else:
        return t

def parse_EXPR_PRIME():
    global lookahead
    if lookahead == '':
        return None
    else:
        if isAnd(lookahead):
            a = parse_AND()
            t = parse_TERM()
            e = parse_EXPR_PRIME()
            if e is not None:
                return (a, merge_prime(t, e))
            else:
                return (a, t)
    
def parse_TERM():
    f = parse_FACTOR()
    t = parse_TERM_PRIME()
    if t is not None:
        return merge_prime(f, t)
    else:
        return f

def merge_func(f1, op, f2):
    if isAnd(op):
        return lambda x : f1(x) and f2(x)
    elif isOr(op):
        return lambda x : f1(x) or  f2(x)
    else:
        error('MERGE_FUNC: unknown op ' + op)

def merge_prime(function, prime):
    if prime is not None:
        op = prime[0]
        f2 = prime[1]
        return merge_func(function, op, f2)
    else:
        return function
    
def isAnd(op):
    return op.lower() in AND_OPTIONS

def isOr(op):
    return op.lower() in OR_OPTIONS
        
def parse_TERM_PRIME():
    global lookahead
    if isAnd(lookahead):
        return None
    elif isOr(lookahead):
        o = parse_OR()
        f = parse_FACTOR()
        t = parse_TERM_PRIME()
        if t is not None:
            return (o, merge_prime(f, t))
        else:
            return (o, f)
    elif lookahead != '' and lookahead != ')':
        error('TERM_PRIME: lookahead is not and or or, its ' + lookahead)
    
def parse_FACTOR():
    global lookahead
    if lookahead == '(':
        advance()
        r = parse_EXPR()
        if lookahead == ')':
            advance()
            return r
        else:
            error('FACTOR: lookahead is not ), its ' + lookahead)
    else:
        return parse_TEST()
    
def parse_TEST():
    global lookahead
    res = parse_CHOICE()
    if lookahead == '!=':
        negate = True
    elif lookahead == '==':
        negate = False
    else:
        error('TEST: lookahead is not ! or =, its ' + lookahead)
    advance()
    string = parse_STRING()
    f = lambda d : True if re.match(string, d[res], re.I) is not None else False
    if negate:
        return lambda d : not f(d)
    else:
        return f

def parse_AND():
    global lookahead
    if not isAnd(lookahead):
        error('AND: lookahead is not and, its ' + lookahead)
    advance()
    return 'and'

def parse_OR():
    global lookahead
    if not isOr(lookahead):
        error('OR: lookahead is not or, its ' + lookahead)
    advance()
    return 'or'
    
def parse_CHOICE():
    global lookahead, choices
    l = lookahead
    if l not in choices:
        error('CHOICE: lookahead is not choice, its ' + lookahead)
    choices[l] += 1
    if choices[l] > 1:
        error('CHOICE: cannot have two of ' + l)
    advance()
    return l
    
def parse_STRING():
    global lookahead
    r = re.sub('\*', '.*', lookahead)
    advance()
    return r

def error(msg):
    print(msg)
    sys.exit(1)

if __name__ == '__main__':
    tests = [
        #        'a==b==c',
        'Kind == foo',
        'Room != foo',
        'World == X and Name != bar',
        'Name != home or Room == Y',
        '( Room == X )',
        '( World == X and Room != Y )',
        'World != Tallon Overworld North',
        'World!=Tallon Overworld|Room==North Pole&Kind == Space Ship and Name!=foo'
    ]

    # query = sys.argv[1]
    l = [
        {
            'Kind':'foo',
            'Room':'foo',
            'World':'foo',
            'Name':'foo'
        },
        {
            'Kind':'bar',
            'Room':'bar',
            'World':'bar',
            'Name':'bar'
        },
        {
            'Kind':'bar',
            'Room':'foo',
            'World':'X',
            'Name':'foo'
        },
        {
            'Kind':'bar',
            'Room':'X',
            'World':'Z',
            'Name':'home'
        }        
    ]
    for query in tests:
        initialize(query)
        func = parse_START()
        print('\n'.join(str(e) for e in l if func(e)))
        print('='*40)
