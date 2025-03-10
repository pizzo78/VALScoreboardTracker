import configparser
import json

def create_config():
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['General'] = {'team': 'NOVO', 'players': [], 'teamSorting': 'false', 'maps': ["Haven", "Fracture", "Bind", "Ascent", "Icebox", "Split", "Breeze", "Lotus", "Pearl", "Sunset", "Abyss"]}

    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    return read_config()

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('config.ini')

    # Access values from the configuration file
    teamSorting = config.getboolean('General', 'teamSorting')
    team = config.get('General', 'team')

    players = json.loads(config.get('General', 'players'))

    # Return a dictionary with the retrieved values
    config_values = {
        'teamSorting': teamSorting,
        'team': team,
        'players': players,
    }

    return config_values
