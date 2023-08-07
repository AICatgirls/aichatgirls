import requests
import chatHistory
import asyncio
import settings

API_ENDPOINT="http://127.0.0.1:5000/api/v1/generate"
MODEL_MAX_TOKENS = 8000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

async def generate_prompt_response(message, character, context):
    chat_history = chatHistory.load_chat_history(message.author, character)
    user_settings = settings.load_user_settings(message.author, character.name)
    prompt = (context + "\n" + chat_history[-MAX_CHAT_HISTORY_LENGTH:] + "\n" +
              f"{message.author.display_name}: {message.content}\n" +
              f"{character.name}: ")
    response = requests.post(
        API_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json={
            "prompt": prompt,
            "max_new_tokens": user_settings["max_new_tokens"],
            "temperature": user_settings["temperature"],
            "repetition_penalty": user_settings["repetition_penalty"],
            "stopping_strings": [f"{message.author.display_name}:"]
        }
    )
    print(prompt)
    print(message.author.display_name)
    response_json = None
    while not response_json:
        response_json = response.json()
        if len(response_json["results"]) > 0:
            text_response = response_json["results"][0]["text"]
        else:
            text_response = "Sorry, I couldn't generate a response."
        await asyncio.sleep(1)  # wait for 1 second before checking again
        
    # Append the original message and text response to the chat history
    chat_history += f"\n{message.author.name}: {message.content}\n{character.name}: {text_response}"
    chatHistory.save_chat_history(chat_history)
    settings.save_user_settings(message.author, character.name, user_settings)
    return text_response
