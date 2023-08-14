import requests
import chatHistory
import asyncio
import settings
import json

API_ENDPOINT="http://127.0.0.1:5000/api/v1/generate"
MODEL_MAX_TOKENS = 8000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

async def generate_prompt_response(message, character, context):
    chat_history = chatHistory.ChatHistory(message, character.name).load(character)
    user_settings = settings.load_user_settings(message.author, character.name)
    prompt = (context + 
              "\n" + chat_history[-MAX_CHAT_HISTORY_LENGTH:] + 
              "\n" + message.author.display_name + ": " + message.content +
              "\n" + character.name + ":" + user_settings["prefix"]).lstrip()
    response = requests.post(
        API_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json={
            "prompt": prompt,
            "max_new_tokens": user_settings["max_response_length"],
            "min_length": user_settings["min_length"],
            "temperature": user_settings["temperature"],
            "repetition_penalty": user_settings["repetition_penalty"],
            "stopping_strings": [f"{message.author.display_name}:"],
            "add_bos_token": False,
        }
    )
    print(f"Incoming message from {message.author.display_name}")
    response_json = None
    while not response_json:
        response_json = response.json()
        if len(response_json["results"]) > 0:
            print(f"Response received for {message.author.display_name}")
            text_response = response_json["results"][0]["text"].lstrip()
        else:
            text_response = "Sorry, I couldn't generate a response."
        await asyncio.sleep(1)  # wait for 1 second before checking again
        
    # Append the original message and text response to the chat history
    updated_chat_history = (
        chat_history + f"\n{message.author.name}: {message.content}\n{character.name}: {text_response}"
    )
    chatHistory.ChatHistory(message, character.name).save(updated_chat_history)
    settings.save_user_settings(message.author, character.name, user_settings)
    return text_response
