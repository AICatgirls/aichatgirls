import os
import json

SETTINGS_FOLDER = "settings"

def create_settings_folder_if_needed():
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
            try:
                loaded_settings = json.load(settings_file)
            except json.JSONDecodeError:
                loaded_settings = {}  # Reset if file is corrupted
    else:
        loaded_settings = {}

    # Ensure all default settings exist in the loaded settings
    updated = False
    for key, value in default_settings.items():
        if key not in loaded_settings:
            loaded_settings[key] = value
            updated = True  # Mark for saving

    # Save back the corrected settings if needed
    if updated:
        save_user_settings(user_id, character_name, loaded_settings)

    return loaded_settings

def handle_setting_command(user_id, character, args):
    if len(args) < 2:
        return """
        Invalid usage. Usage: /set [setting] [value]
        Valid settings are:
            max_response_length - How long the response can be. Shorter responses generate faster.
            min_length - Force the bot to talk longer. Default 1
            temperature - A number between 0.1 and 1.0, default 0.5. The higher the number the more creative the response.
            repetition_penalty - A number between 0.1 and 1.9, default 1.18.
            prefix - A hidden phrase that the bot will silently say before giving a response
        """

    setting = args[1]
    value = args[2] if len(args) > 2 else None  # Allow resetting to default if no value is provided
    settings = load_user_settings(user_id, character.name)

    # Validate setting existence using default settings
    default_settings = {
        "max_response_length": 400,
        "min_length": 12,
        "temperature": 1,
        "repetition_penalty": 1.18,
        "prefix": '',
    }
    
    if setting not in default_settings:
        return "Invalid setting. Valid settings are:\n" + "\n".join(default_settings.keys())

    # If no value is provided, reset to default
    if value is None:
        settings.pop(setting, None)  # Remove user override
        save_user_settings(user_id, character.name, settings)
        return f"Setting '{setting}' reset to its default value."

    # Handle numeric settings with range checks
    valid_ranges = {
        "max_response_length": (1, 4000),
        "min_length": (1, 4000),
        "temperature": (0.1, 2.0),
        "repetition_penalty": (0.1, 1.9),
    }
    
    if setting in valid_ranges:
        try:
            value = float(value)
            min_value, max_value = valid_ranges[setting]
            if not (min_value <= value <= max_value):
                return f"Invalid value for '{setting}'. Must be between {min_value} and {max_value}."
        except ValueError:
            return f"Invalid value for '{setting}'. Must be a number."

    # Save updated setting
    old_value = settings.get(setting, "not set")
    settings[setting] = value
    save_user_settings(user_id, character.name, settings)

    return f"Setting '{setting}' updated from '{old_value}' to '{value}'"

def save_user_settings(user_id, character_name, settings):
    create_settings_folder_if_needed()
    settings_path = os.path.join(SETTINGS_FOLDER, f"{user_id}_{character_name}.json")
    with open(settings_path, "w") as settings_file:
        json.dump(settings, settings_file, indent=4)
