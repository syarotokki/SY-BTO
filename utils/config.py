import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_config(guild_id):
    config = load_config()
    return config.get(str(guild_id))

def set_config(guild_id, data):
    config = load_config()
    config[str(guild_id)] = data
    save_config(config)

def get_log_channel():
    return None
