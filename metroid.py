#!/usr/bin/python3

# Functionality for collectible query database for video game Metroid Prime

import json, argparse, sys
from parsing import QueryParser

class Database():
    """Mechanism for storing and querying items"""

    choices = {'kind', 'room', 'world', 'name', 'found'}

    def __init__(self, dictlist=None):
        self.parser = QueryParser(Database.choices)
        if dictlist is not None:
            self.dicn = { "itemlist" : dictlist }

    @property
    def items(self):
        return self.dicn['itemlist']

    def sort(self, key=None, reverse=False):
        self.items.sort(key=key, reverse=reverse)

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return '\n'.join(str(i) for i in self.items)

    def __repr__(self):
        core = '\n'.join(str(i) for i in self.items)
        return '{\n\"itemlist\":[\n%s\n]\n}' % core

    def parse_json(self, filename):
        """Parse items in filename into database"""
        self.source = filename
        with open(filename, 'r') as f:
            dicn = json.load(f)
        self.dicn = dicn

    def query(self, string, exclude_found, update):
        """Query database for all items satisfying constraints"""
        func = self.parser.parse(string)
        if exclude_found:
            test = lambda x : func(x) and x["found"] == False
        else:
            test = func
        if update:
            for idx, e in enumerate(self.items):
                if test(e):
                    self.dicn['itemlist'][idx]['found'] = True
            with open(self.source, 'w') as stream:
                output(self, stream, json_formatter)
        dictlist = [e for e in self.items if test(e)]
        return Database(dictlist)

def output(database, stream, formatter):
    """Print database to stream f with formatter"""
    formatter(stream, database)

def json_formatter(stream, database):
    json.dump(database.dicn, stream, indent=2)

def html_formatter(stream, database):
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
                        help    = 'the column to sort the output on: One of found, name, kind, room, world'),
    parser.add_argument('-f',
                        choices = make_choices(['none', 'json', 'html']),
                        default = 'n',
                        dest    = 'form',
                        metavar = 'FORMAT',
                        help    = 'the format of the output: One of (n)one, (j)son, (h)tml')
    parser.add_argument('-q',
                        dest    = 'query_string',
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
    db = Database()
    db.parse_json(args.database)
    results = db.query(args.query_string, args.d, args.u)
    if args.sort_order is not None:
        results.sort(key=lambda x : x[args.sort_order])
    if args.output_file is not None:
        stream = open(args.output_file, 'w')
    else:
        stream = sys.stdout
    if args.c:
        count = len(results)
        if args.form[0] == 'n':
            stream.write(str(count) + '\n')
        elif args.form[0] == 'j':
            stream.write('{ count : %d }' % count)
        elif args.form[0] == 'h':
            stream.write('<!DOCTYPE html>\n')
            stream.write('<html><body>\n')
            stream.write('   Query %s returned %d items\n' % (args.query_string, count))
            stream.write('</html></body>\n')
        else:
            print('error: unknown format', args.form)
    else:
        if args.form[0] == 'n':
            output('\n'.join(str(e) for e in results.items), stream, lambda f, s : f.write(s))
        elif args.form[0] == 'j':
            output(results, stream, json_formatter)
        elif args.form[0] == 'h':
            output(results.items, stream, html_formatter)
        else:
            print('error: unknown format', args.form)
    stream.close()
