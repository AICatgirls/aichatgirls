import chatHistory

def chat_command(command, message, character):
    if command == "!reset":
        chatHistory.reset_chat_history(message.author, character.name)
        return "Chat history has been reset."
    elif command == "!help":
        # Add a list of available commands here
        return "Available commands:\n!reset - Resets chat history.\n!help - Shows list of available commands."
    else:
        return "Unknown command. Type !help for a list of available commands."
