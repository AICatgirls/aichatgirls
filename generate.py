import os
import json
import datetime
import requests
import openai
import chatHistory
import settings
from dotenv import load_dotenv

load_dotenv()

# --- Constants & Configuration ---
API_ENDPOINT = os.getenv("OOBABOOGA_API_ENDPOINT", "http://127.0.0.1:5000/v1/completions")

MODEL_MAX_TOKENS = 190000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# --- Helper Functions ---

def build_prompt(context, chat_history, user_display_name, message_content, character_name, prefix):
    """
    Construct the full text prompt from the current and previous messages.
    """
    formatted_history = "\n".join(
        f"{msg['user']}: {msg['message']}"
        for msg in chat_history[-MAX_CHAT_HISTORY_LENGTH:]
    )
    prompt = (
        f"{context}\n"
        f"{formatted_history}\n"
        f"{user_display_name}: {message_content}\n"
        f"{character_name}: {prefix}"
    )
    return prompt

def moderate_input_with_requests(message_content):
    """
    Uses direct HTTP to call OpenAI's moderation endpoint.
    Returns a dict containing 'results' with flagged info or an 'error' key if something goes wrong.
    """
    url = "https://api.openai.com/v1/moderations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    data = {"input": message_content}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()  # Must contain 'results' with 'flagged'
    except requests.RequestException as e:
        print(f"Error calling Moderation endpoint: {e}")
        return {"error": str(e)}

def call_openai(context, prompt, user_settings, message_content):
    """
    Demonstration of the new openai.chat.completions interface in openai>=1.0.0.
    """
    # 1) Moderation check (using direct HTTP request)
    moderation_data = moderate_input_with_requests(message_content)
    if "error" in moderation_data:
        return f"An error occurred while checking moderation: {moderation_data['error']}"

    moderation_result = moderation_data.get("results", [{}])[0]
    if moderation_result.get("flagged"):
        print("Input violates usage policies.")
        return "Sorry, but your input violates content guidelines."

    # 2) If moderation passes, use Chat Completions
    try:
        # Note the new usage: openai.chat.completions.create instead of openai.ChatCompletion.create
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            max_tokens=user_settings["max_response_length"],
            temperature=user_settings["temperature"],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while calling OpenAI: {e}"

def call_oobabooga(prompt, user_settings, user_display_name):
    """
    Calls the Oobabooga API endpoint with a JSON payload for chat/instruct mode.
    Returns the text response or a fallback message on errors.
    """
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "mode": "chat-instruct",
        "prompt": prompt,
        "max_tokens": user_settings["max_response_length"],
        "temperature": user_settings["temperature"],
        "min_tokens": user_settings["min_length"],
        "repetition_penalty": user_settings["repetition_penalty"],
        "stopping_strings": [f"{user_display_name}:"],
        "stop": [f"{user_display_name}:"],
        "max_context_length": MODEL_MAX_TOKENS,
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        if "choices" in response_json and response_json["choices"]:
            return response_json["choices"][0]["text"].strip()
        else:
            return "Sorry, I couldn't generate a response."
    except requests.exceptions.RequestException as req_err:
        return f"An error occurred while calling Oobabooga: {req_err}"

# --- Main Function ---
async def generate_prompt_response(message, character, context):
    print(f"Incoming message from {message.author.display_name}")

    # 1) Initialize and load chat history
    chat_history_instance = chatHistory.ChatHistory(message, character.name)
    chat_history_data = chat_history_instance.load(character, message.author.display_name)

    # 2) Load user settings
    user_settings = settings.load_user_settings(message.author, character.name)
    prefix = user_settings.get("prefix", "").strip()

    # 3) Build the prompt
    prompt = build_prompt(
        context=context,
        chat_history=chat_history_data["messages"],
        user_display_name=message.author.display_name,
        message_content=message.content,
        character_name=character.name,
        prefix=prefix
    )

    # 4) Determine which API to call
    if OPENAI_API_KEY:
        text_response = call_openai(context, prompt, user_settings, message.content)
    else:
        text_response = call_oobabooga(prompt, user_settings, message.author.display_name)

    # 5) Strip off the bot's name if it appears in the response
    character_prefix = f"{character.name}: "
    if text_response.startswith(character_prefix):
        text_response = text_response[len(character_prefix):].strip()

    # 6) Append new messages to chat history
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

    # 7) Save updated chat history
    chat_history_instance.save(chat_history_data)

    return text_response
