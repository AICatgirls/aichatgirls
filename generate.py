import requests
import chatHistory
import settings
import json
import datetime

API_ENDPOINT = "http://127.0.0.1:5000/v1/completions"
MODEL_MAX_TOKENS = 8000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

# Headers for API request
headers = {
    "Content-Type": "application/json",
    # Add your authorization header here if needed
}

async def generate_thinking(character, context, formatted_history, user_settings):
    thinking_prompt = f"{context}\n{formatted_history}\n{character.name} is thinking: "
    thinking_data = {
        "mode": "chat-instruct",
        "prompt": thinking_prompt,
        "max_tokens": 56,
        "temperature": user_settings["temperature"],
        "min_tokens": 4,
        "repetition_penalty": 1,
        "stopping_strings": ["]"],
        "stop": ["]"],
        "max_context_length": 8192,
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=thinking_data)
    return response.json() if response.status_code == 200 else {}

async def generate_response(prompt, user_settings, user_display_name):
    response_data = {
        "mode": "chat-instruct",
        "prompt": prompt,
        "max_tokens": user_settings["max_response_length"],
        "temperature": user_settings["temperature"],
        "min_tokens": user_settings["min_length"],
        "repetition_penalty": user_settings["repetition_penalty"],
        "stopping_strings": [f"{user_display_name}:"],
        "stop": [f"{user_display_name}:"],
        "max_context_length": 8192,
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=response_data)
    return response.json() if response.status_code == 200 else {}

async def generate_prompt_response(message, character, context):
    chat_history_instance = chatHistory.ChatHistory(message, character.name)
    chat_history_data = chat_history_instance.load(character, message.author.display_name)
    user_settings = settings.load_user_settings(message.author, character.name)
    user_display_name = message.author.display_name

    # Prepare chat history for prompts
    chat_history = chat_history_data["messages"]
    formatted_history = []
    for msg in chat_history[-MAX_CHAT_HISTORY_LENGTH:]:
        if msg["user"] == character.name and "thinking" in msg:
            formatted_history.append(f"[{character.name} is thinking: {msg['thinking']}]")
        formatted_history.append(f"{msg['user']}: {msg['message']}")
    formatted_history = "\n".join(formatted_history)

    # Generate "thinking" part
    thinking_json = await generate_thinking(character, context, formatted_history, user_settings)
    thinking_text = thinking_json["choices"][0]["text"].strip() if "choices" in thinking_json else ""
    print(f"{character.name} is thinking: [{thinking_text}]\n")
    
    # Update formatted history with the new thinking text
    formatted_history += f"\n{character.name} is thinking: [{thinking_text}]\n"

    # Construct the prompt for the message response
    prompt = f"{context}\n{formatted_history}\n{message.author.display_name}: {message.content}"
    print(prompt)
    response_json = await generate_response(prompt, user_settings, user_display_name)
    text_response = response_json["choices"][0]["text"].strip() if "choices" in response_json else ""

    # Append the original message, thinking, and text response to the chat history
    new_user_message = {
        "user": message.author.display_name,
        "message": message.content,
        "timestamp": message.created_at.isoformat()
    }
    new_bot_response = {
        "user": character.name,
        "message": text_response,
        "timestamp": datetime.datetime.now().isoformat(),
        "thinking": thinking_text
    }
    chat_history_data["messages"].extend([new_user_message, new_bot_response])
    chat_history_instance.save(chat_history_data)

    return text_response