#!/usr/bin/env python3

'''
Ad-hoc test for query/database implementation
'''

from sys import argv
from parsing import QueryParser

import configuration as config

if __name__ == '__main__':
    # Some crude testing
    tests = [
        '',
        'kind == foo',
        'room != foo',
        'world == X and name != bar',
        'name != home or room == Y',
        '( room == X )',
        '( world == X and room != Y )',
        'world != Tallon Overworld North',
        'world!=Tallon Overworld|room==North Pole&kind==Space Ship and name!=foo'
    ]
    if len(argv) > 1:
        tests.append(argv[1:])
    # mock database
    l = [
        {
            'kind':'Space Ship',
            'room':'North Pole',
            'world': 'Tallon Overworld',
            'name':'bar'
        },
        {
            'kind':'foo',
            'room':'foo',
            'world':'foo',
            'name':'foo'
        },
        {
            'kind':'bar',
            'room':'bar',
            'world':'bar',
            'name':'bar'
        },
        {
            'kind':'bar',
            'room':'foo',
            'world':'X',
            'name':'foo'
        },
        {
            'kind':'bar',
            'room':'X',
            'world':'Z',
            'name':'home'
        }
    ]
    config.loadConfiguration('metroid_prime/config.json')
    for query in tests:
        print('Query:', query)
        parser = QueryParser()
        func = parser.parse(query)
        print('\n'.join(str(e) for e in l if func(e)))
        print('='*40)
