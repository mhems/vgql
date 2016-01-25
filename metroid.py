#!/usr/bin/python3

'''
Functionality for collectible query database for video game Metroid Prime
'''

import argparse, sys
import json

import game

def output(database, stream, formatter):
    '''Print database to stream f with formatter'''
    formatter(stream, database)

def json_formatter(stream, database):
    '''Output database in JSON format to stream'''
    json.dump(database.dicn, stream, indent=2)

def html_formatter(stream, database):
    '''Output database in html format to stream'''
    stream.write('<!DOCTYPE html>\n')
    stream.write('<html><body>\n')
    stream.write('<table>\n')
    stream.write('  <tr>\n')
    stream.write('    <td>Number</td>\n')
    stream.write('    <td>Found</td>\n')
    stream.write('    <td>Name</td>\n')
    stream.write('    <td>Kind</td>\n')
    stream.write('    <td>Room</td>\n')
    stream.write('    <td>World</td>\n')
    stream.write('    <td>Description</td>\n')
    stream.write('  </tr>\n')
    for index, item in enumerate(database):
        stream.write('  <tr>\n')
        stream.write('    <td>%d</td>\n' % (index + 1))
        for element in ['found', 'name', 'kind', 'room', 'world', 'description']:
            if element in item:
                stream.write('    <td>%s</td>\n' % item[element])
            else:
                stream.write('    <td></td>\n')
        stream.write('  </tr>\n')
    stream.write('</table>\n')
    stream.write('</html></body>\n')

def make_choices(choices):
    '''Return list with lowercase choices and first character'''
    first = [s[0].lower() for s in choices]
    low   = [s.lower()    for s in choices]
    return first.extend(low)

if __name__ == '__main__':
    # if invoked with nothing, show help
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    parser = argparse.ArgumentParser(description="Metriod Prime Collectible Query")
    parser.add_argument('-c',
                        action  = 'store_true',
                        default = False,
                        help    = 'return the number of items satisfying the query')
    parser.add_argument('-d',
                        action  = 'store_true',
                        default = False,
                        help    = 'only return those items yet to be found')
    parser.add_argument('-u',
                        action  = 'store_true',
                        help    = 'update matching items to found status')
    parser.add_argument('-o',
                        dest    = 'output_file',
                        metavar = 'OUTPUT_FILE',
                        help    = 'the location of the output file')
    parser.add_argument('-s',
                        choices = ['found', 'name', 'kind', 'room', 'world'],
                        default = 'found',
                        dest    = 'sort_order',
                        metavar = 'SORT_ORDER',
                        help    = 'the column to sort the output on: One of found, name, kind, room, world')
    parser.add_argument('-f',
                        choices = make_choices(['none', 'json', 'html']),
                        default = 'n',
                        dest    = 'form',
                        metavar = 'FORMAT',
                        help    = 'the format of the output: One of (n)one, (j)son, (h)tml')
    parser.add_argument('-q',
                        dest    = 'query_string',
                        default = '',
                        metavar = 'QUERY_STRING',
                        help    = 'the SQL-like query string to execute '
                                  'of the form \'select items where\'...')
    parser.add_argument('database',
                        metavar = 'DATABASE',
                        help    = 'the JSON database to query')
    args = parser.parse_args()
    if args.output_file == args.database:
        print('error: database and output file cannot be the same')
        sys.exit(1)
    db = game.Database()
    db.read(args.database)
    results = db.query(args.query_string, args.d, args.u)
    if args.sort_order is not None:
        results.sort(key=lambda x : x[args.sort_order])
    if args.output_file is not None:
        ostream = open(args.output_file, 'w')
    else:
        ostream = sys.stdout
    if args.c:
        count = len(results)
        if args.form[0] == 'n':
            ostream.write(str(count) + '\n')
        elif args.form[0] == 'j':
            ostream.write('{ count : %d }' % count)
        elif args.form[0] == 'h':
            ostream.write('<!DOCTYPE html>\n')
            ostream.write('<html><body>\n')
            ostream.write('   Query %s returned %d items\n' % (args.query_string, count))
            ostream.write('</html></body>\n')
        else:
            print('error: unknown format', args.form)
    else:
        if args.form[0] == 'n':
            ostream('\n'.join(str(e) for e in results.entries),
                    ostream,
                    lambda f, s : f.write(s))
        elif args.form[0] == 'j':
            ostream(results, ostream, json_formatter)
        elif args.form[0] == 'h':
            ostream(results.entries, ostream, html_formatter)
        else:
            print('error: unknown format', args.form)
    ostream.close()
