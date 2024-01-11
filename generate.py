import requests
import chatHistory
import settings
import json

API_ENDPOINT="http://127.0.0.1:5000/v1/chat/completions"
MODEL_MAX_TOKENS = 8000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

async def generate_prompt_response(message, character, context):
    chat_history = chatHistory.ChatHistory(message, character.name).load(character, message.author.display_name)
    user_settings = settings.load_user_settings(message.author, character.name)
    prompt = (context + 
              "\n" + chat_history[-MAX_CHAT_HISTORY_LENGTH:] + # Limit chat history
              "\n" + message.author.display_name + ": " + message.content +
              "\n" + character.name + ":" + user_settings["prefix"] + " ").lstrip()
    print(prompt)
    
    headers = {
        "Content-Type": "application/json",
        # Add your authorization header here if needed
    }
    
    # Prepare the data for the request
    data = {
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": user_settings["max_response_length"],
        "temperature": user_settings["temperature"],
        "min_tokens": user_settings["min_length"],
        "repetition_penalty": user_settings["repetition_penalty"],
        "stopping_strings": [f"{message.author.display_name}:"],
        "max_context_length": 8192,
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    print(f"Incoming message from {message.author.display_name}")
    
    response_json = response.json()
    if response.status_code == 200 and "choices" in response_json and len(response_json["choices"]) > 0:
        text_response = response_json["choices"][0]["message"]["content"].strip()
    else:
        text_response = "Sorry, I couldn't generate a response."
        print(f"API response error: {response_json}")
        
    # Append the original message and text response to the chat history
    updated_chat_history = (
        chat_history + f"\n{message.author.display_name}: {message.content}\n{character.name}: {text_response}"
    )
    chatHistory.ChatHistory(message, character.name).save(updated_chat_history)
    settings.save_user_settings(message.author, character.name, user_settings)
    return text_response
