'''
Module for handling configurable portions of tools
'''

from json import load

default_file_loc = 'config.json'
config = None

def loadConfiguration(fileloc):
    '''Loads configuration from file location'''
    global config
    with open(fileloc, 'r') as file_:
        conf = load(file_)
    if config is None:
        config = conf
    else:
        config.update(conf)

def get(key):
    '''Gets the configuration value for key '''
    return config[key]

loadConfiguration(default_file_loc)
