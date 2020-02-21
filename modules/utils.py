import json


def get_config():
    try:
        with open("files/config.json") as conf:
            return json.load(conf)
    except OSError:
        print("Configuration not found!\n "
              "Please create a file named 'config.json' into the 'files' directory and follow the setup guide.")
        return None
