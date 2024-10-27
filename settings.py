import os
import json

SETTINGS_FOLDER = "settings"

def create_settings_folder():
    if not os.path.exists(SETTINGS_FOLDER):
        os.makedirs(SETTINGS_FOLDER)

def load_user_settings(user_id, character_name):
    settings_path = os.path.join(SETTINGS_FOLDER, f"{user_id}_{character_name}.json")
    default_settings = {
        "max_response_length": 400,
        "min_length": 12,
        "temperature": 1,
        "repetition_penalty": 1.18,
        "prefix": '',
    }
    
    if os.path.exists(settings_path):
        with open(settings_path, "r") as settings_file:
            loaded_settings = json.load(settings_file)
        
        # Check for missing keys and update with default values if necessary
        for key, value in default_settings.items():
            if key not in loaded_settings:
                loaded_settings[key] = value
        
        return loaded_settings
    else:
        return default_settings

def save_user_settings(user_id, character_name, settings):
    create_settings_folder()
    settings_path = os.path.join(SETTINGS_FOLDER, f"{user_id}_{character_name}.json")
    with open(settings_path, "w") as settings_file:
        json.dump(settings, settings_file)
