#!/usr/bin/python3

# Functionality for collectible query database for video game Metroid Prime

import json, argparse, sys
import query_parser

class Database():
    """Mechanism for storing and querying items"""

    def parse_items(self, filename):
        """Parse items in filename into database"""
        with open(filename, 'r') as f:
            self.__items = json.load(f)

    @property
    def items(self):
        return self.__items['itemlist']

    def print_json(self, filename):
        """Print database to filename in json format"""
        with open(filename, 'w') as f:
            json.dump(self.__items, f, indent=2)

    def print_html(self, filename):
        """Print database to filename in html format"""
        pass

    def query(self, string):
        """Query database for all items satisfying constraints"""
        self.func = query_parser.parse(string)
        return [str(e) for e in self.items if self.func(e)]

    def __len__(self):
        return len(d.items)
    
    def __str__(self):
        return '\n'.join(str(i) for i in self.items)
    
    def __repr__(self):
        return '\n'.join(repr(i) for i in self.items)
    
if __name__ == '__main__':
    # usage ./metroid.py [-c] [-q [-AAAA NNNN]+] [-o FILE] DATABASE
    parser = argparse.ArgumentParser(description="Metriod Prime Collectible Query")
    parser.add_argument('-o', '--output-file',
                        dest    = 'output',
                        default = sys.stdout,
                        metavar = 'OUTPUT_FILE',
                        help    = 'the location of the output file')
    parser.add_argument('-c', '--count',
                        action = 'store_true',
                        default = False,
                        help    = 'return the number of items satisfying the query')
    parser.add_argument('-q', '--query',
                        dest = 'query_string',
                        metavar = 'QUERY_STRING',
                        help    = 'the SQL-like query string to execute '
                                  'of the form \'select items where\'')
    parser.add_argument('database',
                        metavar = 'DATABASE',
                        help    = 'the database to query')
    args = parser.parse_args()
    d = Database()
    d.parse_items(args.database)
    results = d.query(args.query_string)
    if args.count:
        print(len(results))
    else:
        print('\n'.join(results))
