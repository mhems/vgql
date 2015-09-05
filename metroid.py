# Functionality for collectible query database for video game Metroid Prime

import json

class Database():
    """Mechanism for storing and querying items"""

    def parse_items(self, filename):
        """Parse items in filename into database"""
        with open(filename, 'r') as f:
            self.items = json.load(f)

    def print_json(self, filename):
        """Print database to filename in json format"""
        with open(filename, 'w') as f:
            json.dump(self.items, f, indent=2)

    def print_html(self, filename):
        """Print database to filename in html format"""
        pass

    def query(self, **constraints):
        """Query database for all items satisfying constraints"""
        # TODO
        pass

    def __len__(self):
        return len(d.items['itemlist'])
    
    def __str__(self):
        return '\n'.join(str(i) for i in self.items)
    
    def __repr__(self):
        return '\n'.join(repr(i) for i in self.items)
    
if __name__ == '__main__':
    # establish command line options
    # check arguments
    # call appropriate function
    d = Database()
    d.parse_items('all.json')
    d.print_json('test.json')
