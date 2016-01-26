# Video Game Query Language Tool

Command-line tool to maximize efficiency when playing
collectible-driven video games such as Metroid Prime.

These games follow the general formula of a character traversing a map
with interconnected rooms, clustered in interconnected worlds
searching for collectibles. Some are mandatory for game completion
while others are purely supplementary. Collectibles can be partitioned
into two groups: named items and expansions. The character's progress
is dictated by a constrained map that becomes more accessible with the
acquisition of items that allow a dependency to be satisfied. The game
can thus be seen as a course from item to item, picking up expansions
along the way.

The functionality can be split into 2 facets

1. Query tool to track, view, and update database of collectibles you
have found in the game
    * Small DSL SQL-like query strings allow fine-grained filtering
    * Multiple output formats including unaltered, JSON, and html
    * Track your progress by marking collectibles as collected
    * Sort collectibles by aspect
1. Planning tool to determine the shortest path to accomplish a task
   with the collectibles you have so far while avoiding paths that
   require collectibles you have yet to obtain
   * Goal thresholding for expansion-agnostic paths or 100% completion
   * Textual or graphical output of step-by-step directions
   * Single collectible target or plot entire game

Note: This README does not reflect the current progess, rather it is
both documentation for what I've done and what I'd like to do. See the
bottom section for the current state of implementation.

# Requirements
* python3
* pydotplus (pydot port for python3)
  [[PyPi]](https://pypi.python.org/pypi/pydotplus)

# Usage

```
./metroid.py [-h] [-c] [-d] [-u] [-o OUTPUT_FILE] [-s SORT_ORDER]
             [-f FORMAT] [-q QUERY_STRING]
             DATABASE

positional arguments:
  DATABASE         the JSON database to query

optional arguments:
  -h, --help       show this help message and exit
  -c               return the number of items satisfying the query
  -d               only return those items yet to be found
  -u               update matching items to found status
  -o OUTPUT_FILE   the location of the output file
  -s SORT_ORDER    the column to sort the output on: One of found,
                   name, kind, room, world
  -f FORMAT        the format of the output: One of (n)one, (j)son,
                   (h)tml
  -q QUERY_STRING  the SQL-like query string to execute of the form
                   'select items where'...
```

plotting tool coming soon

# Configuration

This tool is configurable per video game, conditional on its
similarity to the formula outlined above. I'm sure there are some
Metroid-specific assumptions that need to be refactored out.

Directory structure of a game this tool should analyze:
* **game_name/**
  * **config.json**
    - customize off of the top-level config.json
  * **data.txt**
    - holds game map and collectibles with locations in this tool's DSL

# Language Specs

The DSL this tool uses to internalize the game's data is specified by
the following grammar, in EBNF notation, with Perl-style regexes:

```
start:      world + ;
world:      WB ID WB room + ;
room:       BG ID dep ? pickup * adj ? ;
pickup:     BULLET pot_pair dep ? how ? ;
how:        INFO ;
adj:        PIPE connection ( COMMA connection ) * ;
connection: ID dep ? loc ? ;
dep:        LP pot_pair ( COMMA pot_pair ) * RP ;
pot_pair:   ID (COLON ID) ? ;
loc:        LB ID RB ;

INFO:   /^\W*-\W*.*\W*$/ ;
ID:     /[a-zA-Z0-9][-a-zA-Z0-9\_ ]*/ ;
BULLET: '*' ;
BG:     '>' ;
WB:     '#' ;
COMMA:  ',' ;
PIPE:   '|' ;
COLON:  ':' ;
LP:     '(' ;
RP:     ')' ;
LB:     '[' ;
RB:     ']' ;
```

The DSL this tool uses as query strings in specified by the following
grammar, in EBNF notation, with Perl-style regexes:

```
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
CHOICE: 'found' | 'kind' | 'name' | 'room' | 'world' ;
```

The punctuation characters should be trivial to modify to your
liking. Parsing is implemented in a recursive top-down fashion.

The lexer is whitespace-insensitive within a line but is newline
sensitive. This could be at times annoying so a newline-agnostic
implementation would be better.

# Acknowledgements

Data and graphs for game collectibles from
[ign](http://www.ign.com/wikis/metroid-prime/) and
[here](http://metroid.retropixel.net/games/mprime/)

# Progress

* The query portion of functionality is fairly implemented, albeit
  crudely tested
* The game module should be parameterizable by game so some config
  code has been added
* Primitive graph algorithms have been added to calculate distances,
  accounting for edges with dependencies and upgrades
* Dependency analysis will be required to plot a course to get the
  determined upgrade, which can be repeated to complete the game
* With the backend complete, a simple command-line tool and graphical
  view will be implemented

# Thoughts

* The 'database' is flat, it should likely be given some structure to
  focus the queries
* The graph, once constructed, does not change - properties and
  calculations should be cached to avoid needless traversal of the
  large structure
