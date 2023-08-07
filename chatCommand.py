import chatHistory
from settings import load_user_settings, save_user_settings

def chat_command(command, message, character):
    if command == "!reset":
        return reset_chat_history(message.author, character.name)

    elif command.startswith("!remove"):
        string_to_remove = message.content.replace(command, "").strip()
        return remove_string_from_chat_history(message.author, character, string_to_remove)

    elif command.startswith("!set"):
        return handle_setting_command(message.author, character, message.content.split(" ")[1:])

    else:
        return """
        Available commands:
        !reset - Resets chat history.
        !remove [text] - Removes all instances of [text] from chat history.
        !set [setting] [value] - Changes user settings
        !help - Shows list of available commands.
        """

def reset_chat_history(user_id, character_name):
    chatHistory.reset_chat_history(user_id, character_name)
    return "Chat history has been reset."

def remove_string_from_chat_history(user_id, character, string_to_remove):
    chat_history = chatHistory.load_chat_history(user_id, character)
    updated_chat_history = chat_history.replace(string_to_remove, "")

    # Clean up punctuation and double spaces
    replacements = {
        "  ": " ",             # Replace multiple spaces with a single space
        " .": ".",             # Replace space followed by a period with just the period
        " ,": ",",             # Replace space followed by a comma with just the comma
        ",.": ".",
        ".,": ",",
        ",,": ",",
    }
    for old, new in replacements.items():
        updated_chat_history = updated_chat_history.replace(old, new)
    for old, new in replacements.items():  # I'm being lazy and just running it twice, rather than adding additional permutations
        updated_chat_history = updated_chat_history.replace(old, new)

    chatHistory.save_chat_history(updated_chat_history)
    return f"All instances of '{string_to_remove}' have been removed from the chat history."

def handle_setting_command(user_id, character, args):
    if len(args) != 2:
        return """
        Invalid usage. Usage: !set [setting] [value]
        Valid settings are:
            max_response_length - How long the response can be. Shorter responses generate faster.
            temperature - A number between 0.1 and 0.9, default 0.5. The higher the number the more creative the response.
            repetition_penalty - A number between 0.1 and 1.9, default 1.18.
        """

    setting, value = args
    settings = load_user_settings(user_id, character.name)

    if setting == "max_response_length":
        try:
            value = int(value)
        except ValueError:
            return "Invalid value for 'max_response_length'. It should be a number."
        settings["max_new_tokens"] = value
        save_user_settings(user_id, character.name, settings)
        return f"Setting 'max_response_length' updated to {value}"

    elif setting == "temperature":
        return handle_float_setting(user_id, character.name, settings, "temperature", value, 0.1, 0.9)

    elif setting == "repetition_penalty":
        return handle_float_setting(user_id, character.name, settings, "repetition_penalty", value, 0.1, 1.9)

    else:
        return """
        Invalid setting. Valid settings are:
            max_response_length - How long the response can be. Shorter responses generate faster.
            temperature - A number between 0.1 and 0.9, default 0.5. The higher the number the more creative the response.
            repetition_penalty - A number between 0.1 and 1.9, default 1.18.
        """

def handle_float_setting(user_id, character_name, settings, setting_name, value, min_value, max_value):
    try:
        value = float(value)
        if not min_value <= value <= max_value:
            raise ValueError
    except ValueError:
        return f"Invalid value for '{setting_name}'. It should be a number between {min_value} and {max_value}."
    settings[setting_name] = value
    save_user_settings(user_id, character_name, settings)
    return f"Setting '{setting_name}' updated to {value}"
