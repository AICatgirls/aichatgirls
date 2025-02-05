from chatHistory import ChatHistory
from settings import load_user_settings, save_user_settings, handle_setting_command
from scripts.whitelist import Whitelist

whitelist = Whitelist()

def chat_command(command, message, character):
    if command == "/whitelist":
        whitelist.add_channel(message.channel.id)
        return f"This channel ({message.channel.name}) has been whitelisted."
        
    elif command == "/help":
        return """
        Available commands:
            /whitelist - allows bot to speak in this channel
            /blacklist - prevents bot from speaking in this channel
            /reset - Resets chat history.
            /remove [text] - Removes all instances of [text] from chat history.
            /set [setting] [value] - Changes user settings
            /help - Shows list of available commands.
        """
        
    elif not whitelist.is_channel_whitelisted(message.channel) and message.channel.name != "local_chat":
        return

    elif command == "/blacklist":
        whitelist.remove_channel(message.channel.id)
        return f"This channel ({message.channel.name}) has been removed from the whitelist."
        
    elif command == "/reset":
        return reset_chat_history(message, character.name)

    elif command.startswith("/remove"):
        string_to_remove = message.content.replace(command, "").strip()
        return remove_string_from_chat_history(message, character, string_to_remove)

    elif command.startswith("/set"):
        return handle_setting_command(message.author, character, message.content.split(" ", 2))

    else:
        return """
        Available commands:
            /whitelist - allows bot to speak in this channel
            /blacklist - prevents bot from speaking in this channel
            /reset - Resets chat history.
            /remove [text] - Removes all instances of [text] from chat history.
            /set [setting] [value] - Changes user settings
            /help - Shows list of available commands.
        """

def reset_chat_history(message, character_name):
    ChatHistory(message, character_name).reset()
    return "Chat history has been reset."

def remove_string_from_chat_history(message, character, string_to_remove):
    chat_history = ChatHistory(message, character.name).load(character, message.author)
    updated_chat_history = chat_history.replace(string_to_remove, "")

    # Clean up punctuation and double spaces
    replacements = {
        "  ": " ",
        " .": ".",
        " ,": ",",
        ",.": ".",
        ".,": ",",
        ",,": ",",
    }
    for old, new in replacements.items():
        updated_chat_history = updated_chat_history.replace(old, new)
    for old, new in replacements.items():
        updated_chat_history = updated_chat_history.replace(old, new)

    ChatHistory(message, character.name).save(updated_chat_history)
    return f"All instances of '{string_to_remove}' have been removed from the chat history."

def default_range(setting_name):
    ranges = {
        "max_response_length": (1, 4000),
        "min_length": (1, 4000),
        "temperature": (0.1, 2.0),
        "repetition_penalty": (0.1, 1.9),
    }
    return ranges.get(setting_name, (0, 0))

def is_float_setting(setting_name):
    return setting_name in ["max_response_length", "min_length", "temperature", "repetition_penalty"]

def handle_float_setting(user_id, character_name, settings, setting_name, value, min_value, max_value):
    try:
        value = float(value)
        if not min_value <= value <= max_value:
            raise ValueError
    except ValueError:
        return f"Invalid value for '{setting_name}'. It should be a number between {min_value} and {max_value}."

    old_value = settings.get(setting_name, "not set")
    settings[setting_name] = value
    save_user_settings(user_id, character_name, settings)
    
    if old_value != "not set":
        return f"Setting '{setting_name}' updated from {old_value} to {value}"
    else:
        return f"Setting '{setting_name}' set to {value}"

def handle_string_setting(user_id, character_name, settings, setting_name, value, default_value):
    old_value = settings.get(setting_name, "not set")
    settings[setting_name] = value
    save_user_settings(user_id, character_name, settings)

    if old_value != "not set":
        return f"Setting '{setting_name}' updated from '{old_value}' to '{value}'"
    else:
        return f"Setting '{setting_name}' set to '{value}'"
