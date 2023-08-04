import chatHistory

def chat_command(command, message, character):
    if command == "!reset":
        chatHistory.reset_chat_history(message.author, character.name)
        return "Chat history has been reset."
    # elif command == "!help":
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
        }
        for old, new in replacements.items():
            updated_chat_history = updated_chat_history.replace(old, new)
        for old, new in replacements.items(): # I'm being lazy and just running it twice, rather than adding additional permutations
            updated_chat_history = updated_chat_history.replace(old, new)
        
        # Save the updated chat history
        chatHistory.save_chat_history(updated_chat_history)
        
        return f"All instances of '{string_to_remove}' have been removed from the chat history."
    else:
        return "Available commands:\n!reset - Resets chat history.\n!remove [text] - Removes all instances of [text] from chat history.\n!help - Shows list of available commands."
