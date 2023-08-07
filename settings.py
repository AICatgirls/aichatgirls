import os
import json

SETTINGS_FOLDER = "settings"

def create_settings_folder():
    if not os.path.exists(SETTINGS_FOLDER):
        os.makedirs(SETTINGS_FOLDER)

def load_user_settings(user_id, character_name):
    settings_path = os.path.join(SETTINGS_FOLDER, f"{user_id}_{character_name}.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as settings_file:
            return json.load(settings_file)
    else:
        # Return default settings if the settings file doesn't exist
        return {
            "max_new_tokens": 400,
            "temperature": 0.5,
            "repetition_penalty": 1.18,
        }

def save_user_settings(user_id, character_name, settings):
    create_settings_folder()
    settings_path = os.path.join(SETTINGS_FOLDER, f"{user_id}_{character_name}.json")
    with open(settings_path, "w") as settings_file:
        json.dump(settings, settings_file)
