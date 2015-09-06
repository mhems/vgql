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
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    parser = argparse.ArgumentParser(description="Metriod Prime Collectible Query")
    parser.add_argument('-c',
                        action = 'store_true',
                        default = False,
                        help    = 'return the number of items satisfying the query')
    parser.add_argument('-o',
                        dest    = 'output_file',
                        metavar = 'OUTPUT_FILE',
                        help    = 'the location of the output file')
    parser.add_argument('-q',
                        dest = 'query_string',
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
    d = Database()
    d.parse_items(args.database)
    results = d.query(args.query_string)
    if args.count:
        output = str(len(results))
    else:
        output = '\n'.join(results)
    if args.output_file is not None:
        with open(args.output_file, 'w') as f:
            f.write(output)
            f.write('\n')
    else:
        print(output)
