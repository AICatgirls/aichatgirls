import chatHistory
from settings import load_user_settings, save_user_settings

def chat_command(command, message, character):
    if command == "!reset":
        chatHistory.reset_chat_history(message.author, character.name)
        return "Chat history has been reset."
        
    elif command.startswith("!remove"):
        string_to_remove = message.content.replace(command, "").strip()
        
        # Load the chat history
        chat_history = chatHistory.load_chat_history(message.author, character)
        
        # Remove all instances of the specified string from the chat history
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
        for old, new in replacements.items(): # I'm being lazy and just running it twice, rather than adding additional permutations
            updated_chat_history = updated_chat_history.replace(old, new)
        
        # Save the updated chat history
        chatHistory.save_chat_history(updated_chat_history)
        
        return f"All instances of '{string_to_remove}' have been removed from the chat history."
        
    elif command.startswith("!set"):
        args = message.content.split(" ")[1:]  # Remove the command itself
        if len(args) != 2:
            return """
            Invalid usage. Usage: !set [setting] [value]
            Valid settings are:
                max_response_length - How long in tokens the response can be, default 400.
                temperature - A number between 0.1 and 1.9, default 1. The higher the number the more creative the response.
                repetition_penalty - A number between 0.1 and 1.9, default 1.18.
            """
        setting, value = args
        if setting == "max_response_length":
            try:
                value = int(value)
            except ValueError:
                return "Invalid value for 'max_response_length'. It should be a number."
            settings = load_user_settings(message.author, character.name)
            settings["max_new_tokens"] = value
            save_user_settings(message.author, character.name, settings)

            return f"Setting 'max_response_length' updated to {value}"
        elif setting == "temperature":
            try:
                value = float(value)
                if not 0.1 <= value <= 1.9:
                    raise ValueError
            except ValueError:
                return "Invalid value for 'temperature'. It should be a number between 0.1 and 1.9."
            settings = load_user_settings(message.author, character.name)
            settings["temperature"] = value
            save_user_settings(message.author, character.name, settings)

            return f"Setting 'temperature' updated to {value}"
        elif setting == "repetition_penalty":
            try:
                value = float(value)
                if not 0.1 <= value <= 1.9:
                    raise ValueError
            except ValueError:
                return "Invalid value for 'repetition_penalty'. It should be a number between 0.1 and 1.9."
            settings = load_user_settings(message.author, character.name)
            settings["repetition_penalty"] = value
            save_user_settings(message.author, character.name, settings)

            return f"Setting 'repetition_penalty' updated to {value}"
        else: 
            return """
            Invalid setting. Valid settings are:
                max_response_length - How long in tokens the response can be, default 400.
                temperature - A number between 0.1 and 1.9, default 1. The higher the number the more creative the response.
                repetition_penalty - A number between 0.1 and 1.9, default 1.18.
            """
    else:
        return """
        Available commands:
        !reset - Resets chat history.
        !remove [text] - Removes all instances of [text] from chat history.
        !set [setting] [value] - Changes user settings
        !help - Shows list of available commands.
        """
