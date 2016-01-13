# Metroid Prime Collectible Query Tool

Command-line tool for maintaining and filtering list of collectibles
in the video game Metroid Prime.

Offers a variety of features including:
* Small DSL SQL-like query strings allow fine-grained filtering
* Multiple output formats including unaltered, JSON, and html
* Track your progress by marking collectibles as collected
* Sort collectibles by aspect

This is a small exercise in writing some code for an idea I had,
giving me a chance to write a simple parser and attribute grammar
framework where a filter function is synthesized during parsing.

Right now, there are no formal tests for this tool. With little
effort, this tool should be able to be configurable per video game and
aspect so players can use this tool for multiple games

Data for game collectibles was scraped from
[ign](http://www.ign.com/wikis/metroid-prime/) and
[here](http://metroid.retropixel.net/games/mprime/)
