# Background color of generated map
background = 'black'

# Color associations of door types
door_color_map = {
    'default' : 'blue',
    'missile' : 'grey',
    'wave' : 'purple',
    'ice' : 'white',
    'plasma' : 'red'
}

# Color associations of worlds
world_color_map = {
    'Tallon Overworld' : 'green',
    'Chozo Ruins' : 'orange',
    'Magmoor Caverns' : 'red',
    'Phendrana Drifts' : 'white',
    'Phazon Mines' : 'grey',
    'Impact Crater' : 'purple',
    'Elevator' : 'yellow'
}

# List of worlds
worlds = [
    'Pirate Frigate',
    'Tallon Overworld',
    'Chozo Ruins',
    'Magmoor Caverns',
    'Phendrana Drifts',
    'Phazon Mines',
    'Impact Crater'
]

# Kinds of collectibles
kinds = [
    'Artifact',
    'Boss',
    'Chozo Lore',
    'Creature',
    'Energy Tank',
    'Missile Expansion',
    'Pirate Data',
    'Power Bomb Expansion',
    'Research',
    'Upgrade'
]

# Choices (variables) available in query string
choices = [
    'kind',
    'room',
    'world',
    'name',
    'found'
]
