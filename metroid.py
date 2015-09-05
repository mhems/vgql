# Functionality for collectible query database for video game Metroid Prime


class Collectible():
    """Simple POD for collectibles"""

    # name  - the name of the collectible
    # room  - the room the Collectible is located in
    # world - the world the Collectible is located in
    # kind  - the kind of Collectible
    # desc  - optional description on how to obtain collectible
    def __init__(self, name, room, world, kind, desc=None):
        self.name  = name
        self.room  = room
        self.world = world
        self.kind  = kind
        self.desc  = desc

    def __str__(self):
        msg = 'Description: %s\n' % self.desc if self.desc else ''
        return ( 'Collectible: %s\n'
                 'Location:    %s, %s\n'
                 'Kind:        %s\n'
                 '%s' % (self.name , self.room, self.world, self.kind, msg) )

    def __repr__(self):
        msg = '"Description": %s\n' % self.desc if self.desc else ''
        return ( '{\n"Name": %s\n'
                 '"Room": %s\n'
                 '"World": %s\n'
                 '"Kind": %s\n'
                 '%s}\n' % (self.name, self.room, self.world, self.kind, msg) )
    
class Expansion():
    """Simple POD for expansions"""

    # room  - the room the Expansion is located in
    # world - the world the Expansion is located in
    # kind  - the kind of Expansion
    # desc  - optional description on how to obtain expansion
    def __init__(self, room, world, kind, desc=None):
        self.room  = room
        self.world = world
        self.kind  = kind
        self.desc  = desc

    def __str__(self):
        msg = 'Description: %s\n' % self.desc if self.desc else ''
        return ( 'Expansion:   %s\n'
                 'Location:    %s, %s\n'
                 '%s' % (self.kind, self.room, self.world, msg) )

    def __repr__(self):
        msg = '"Description": %s\n' % self.desc if self.desc else ''
        return ( '{\n"Room": %s\n'
                 '"World": %s\n'
                 '"Kind": %s\n'
                 '%s}\n' % (self.room, self.world, self.kind, msg) )

class Item():
    """Simple POD for Items"""

    # room  - the room the Item is located in
    # world - the world the Item is located in
    # kind  - the kind of Item
    # name  - optional name of the item
    # desc  - optional description on how to obtain item
    def __init__(self, room, world, kind, name=None, desc=None):
        self.room  = room
        self.world = world
        self.kind  = kind
        self.name  = name
        self.desc  = desc

    def __str__(self):
        msg = ''
        if self.name is not None:
            msg += 'Name: %s\n' % self.name
        msg += ( 'Kind:   %s\n'
                 'Location:    %s, %s\n' % (self.kind, self.room, self.world) )
        if self.desc is not None:
            msg += 'Description: %s\n' % self.desc
        return msg

    def __repr__(self):
        msg = '{\n'
        if self.name is not None:
            msg += 'Name: %s\n' % self.name
        msg += ( 'Kind:   %s\n'
                 'Location:    %s, %s\n' % (self.kind, self.room, self.world) )
        if self.desc is not None:
            msg += 'Description: %s\n' % self.desc
        return msg + '}\n'
    
class Database():
    """Mechanism for storing and querying items"""

    def __init__(self):
        self.items = []

    def add(self, item):
        """Add item to database"""
        self.items.append(item)

    def remove(self, item):
        """Remove item from database"""
        self.items.remove(item)
        
    def parse_items(self, filename):
        """Parse items in filename into database"""
        # TODO
        pass

    def print_json(self, filename):
        """Print database to filename in json format"""
        with open(filename, 'w') as f:
            f.write(repr(self))

    def print_html(self, filename):
        """Print database to filename in html format"""
        pass

    def query(self, **constraints):
        """Query database for all items satisfying constraints"""
        # TODO
        pass

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
    print(repr(d))
