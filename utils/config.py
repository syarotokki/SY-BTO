import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_guild_config(guild_id):
    config = load_config()
    return config.get(str(guild_id), {})

def set_guild_config(guild_id, youtube_channel_id=None, channel_id=None, log_channel_id=None):
    config = load_config()
    guild_id = str(guild_id)

    if guild_id not in config:
        config[guild_id] = {}

    if youtube_channel_id is not None:
        config[guild_id]["youtube_channel_id"] = youtube_channel_id
    if channel_id is not None:
        config[guild_id]["channel_id"] = channel_id
    if log_channel_id is not None:
        config[guild_id]["log_channel_id"] = log_channel_id

    save_config(config)
