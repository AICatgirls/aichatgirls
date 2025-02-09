import chatHistory
import datetime
import json
import openai
import os
import requests
import settings

from dotenv import load_dotenv
load_dotenv()

# Todo: move these into the .env file
API_ENDPOINT="http://127.0.0.1:5000/v1/completions"
MODEL_MAX_TOKENS = 190000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    client = openai.Client(api_key=OPENAI_API_KEY)

async def generate_prompt_response(message, character, context):
    # Initialize ChatHistory instance
    chat_history_instance = chatHistory.ChatHistory(message, character.name)
    chat_history_data = chat_history_instance.load(character, message.author.display_name)
    user_settings = settings.load_user_settings(message.author, character.name)
    prefix = user_settings.get("prefix","").strip()

    # Construct the prompt
    chat_history = chat_history_data["messages"]
    formatted_history = "\n".join([f"{msg['user']}: {msg['message']}" for msg in chat_history[-MAX_CHAT_HISTORY_LENGTH:]])
    prompt = (
        context + "\n" +
        formatted_history + "\n" +
        message.author.display_name + ": " + message.content + "\n" +
        character.name + ": " + prefix
    )

    # Prepare headers for API request
    headers = {
        "Content-Type": "application/json",
        # Add your authorization header here if needed
    }
    
    print(f"Incoming message from {message.author.display_name}")

    # Choose between Oobabooga and OpenAI based on whether OPENAI_API_KEY is set
    if OPENAI_API_KEY:
        # OpenAI API call
        try:
            moderation_response = client.moderations.create(input=message.content)
            moderation_result = moderation_response.results[0]
            if moderation_result.flagged:
                print("Input violates usage policies.")
                text_response = "Sorry, but your input violates content guidelines."
            else:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=user_settings["max_response_length"],
                    temperature=user_settings["temperature"]
                )
                text_response = response.choices[0].message.content.strip()
        except Exception as e:
            text_response = f"An error occurred: {e}"
    else:
        # Send the API request to Oobabooga
        data = {
            "mode": "chat-instruct",
            "prompt": prompt,
            "max_tokens": user_settings["max_response_length"],
            "temperature": user_settings["temperature"],
            "min_tokens": user_settings["min_length"],
            "repetition_penalty": user_settings["repetition_penalty"],
            "stopping_strings": [f"{message.author.display_name}:"],
            "stop": [f"{message.author.display_name}:"],
            "max_context_length": MODEL_MAX_TOKENS,
        }
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        response_json = response.json()
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200 and "choices" in response_json and len(response_json["choices"]) > 0:
            text_response = response_json["choices"][0]["text"].strip()
        else:
            text_response = "Sorry, I couldn't generate a response."

    # Strip off the bot's name from the response
    character_prefix = f"{character.name}: "
    if text_response.startswith(character_prefix):
        text_response = text_response[len(character_prefix):].strip()

    # Append the original message and text response to the chat history
    new_user_message = {
        "user": message.author.display_name,
        "message": message.content,
        "timestamp": message.created_at.isoformat()
    }
    new_bot_response = {
        "user": character.name,
        "message": text_response,
        "timestamp": datetime.datetime.now().isoformat()
    }
    chat_history_data["messages"].extend([new_user_message, new_bot_response])
    
    # Save the updated chat history
    chat_history_instance.save(chat_history_data)

    return text_response
