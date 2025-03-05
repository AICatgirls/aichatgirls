import os
import json
import datetime
import requests
import openai
from characterState import update_character_state
import chatHistory
import concurrent.futures
import settings
from dotenv import load_dotenv
import loadCharacterCard

load_dotenv()

# --- Constants & Configuration ---
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://127.0.0.1:5000/v1/completions")

MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", "190000"))
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# --- Helper Functions ---

def build_prompt(chat_history, user_display_name, message_content, character_name, prefix):
    """
    Construct the full text prompt from the current and previous messages.
    """
    formatted_history = "\n".join(
        f"{msg['user']}: {msg['message']}"
        for msg in chat_history[-MAX_CHAT_HISTORY_LENGTH:]
    )
    prompt = (
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
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        response_json = response.json()

        if "results" not in response_json:
            return {"error": "Unexpected response format. Missing 'results' key."}

        return response_json
    except requests.RequestException as e:
        print(f"Error calling Moderation endpoint: {e}")
        return {"error": str(e)}

def generate_openai_response(
    context: str,
    prompt: str,
    max_tokens: int = 50,
    temperature: float = 0.1
) -> str:
    """
    Calls the OpenAI chat completion endpoint using the given context and prompt.
    max_tokens and temperature have default fallback values (50 and 0.1 respectively).
    Returns the response text or an error message if something goes wrong.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while calling OpenAI: {e}"

def call_openai(context, prompt, user_settings, message_content):
    # 1) Moderation check (using direct HTTP request)
    moderation_data = moderate_input_with_requests(message_content)
    if "error" in moderation_data:
        return f"An error occurred while checking moderation: {moderation_data['error']}"

    moderation_result = moderation_data.get("results", [{}])[0]
    if moderation_result.get("flagged"):
        print("Input violates usage policies.")
        return "Sorry, but your input violates content guidelines."

    # 2) If moderation passes, use Chat Completions
    return generate_openai_response(
        context=context,
        prompt=prompt,
        max_tokens=user_settings["max_response_length"],
        temperature=user_settings["temperature"]
    )

def call_oobabooga(context, prompt, user_settings=None, user_display_name=None):
    """
    Calls the Oobabooga API endpoint with a JSON payload for chat-instruct mode.
    Returns the text response or a fallback message on errors.
    """
    if user_settings is None:
        user_settings = {}
    if user_display_name is None:
        user_display_name = "User"
    
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "mode": "chat-instruct",
        "prompt": f"{context}\n{prompt}",
        "max_tokens": user_settings.get("max_response_length", 50),  # default to 50
        "temperature": user_settings.get("temperature", 0.1),         # default to 0.1
        "min_tokens": user_settings.get("min_length", 1),              # default if not provided
        "repetition_penalty": user_settings.get("repetition_penalty", 1.0),  # default if not provided
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

def get_last_state_value(messages, state_key, bot_name):
    """
    Iterates over messages in reverse order to find the most recent bot message
    that contains a value for the given state_key.
    """
    for msg in reversed(messages):
        if msg.get("user") == bot_name and state_key in msg:
            return msg[state_key]
    return ""  # Default to empty string if not found

# --- Main Function ---
async def generate_prompt_response(message):
    """
    Generates a response for the given message by:
      1. Loading the user's Character (with fallback)
      2. Building the context
      3. Managing the chat history
      4. Calling the LLM (OpenAI or Oobabooga)
      5. Saving the updated chat history
    """
    print(f"Incoming message from {message.author.display_name}")

    # 1) Load the Character
    #    Use the user's ID (or some unique string) + a fallback name like "Felicia".
    user_id = str(message.author.id)
    character = loadCharacterCard.Character.load_character_card(user_id, "Felicia", use_openai=bool(OPENAI_API_KEY))

    # 2) Build the context from the Character's data
    context = (
        f"Name: {character.name}\n"
        f"Description: {character.description}\n"
        f"Personality: {character.personality}"
    )

    # 3) Initialize and load chat history
    #    We'll just pass the character's name for identification in the history.
    chat_history_instance = chatHistory.ChatHistory(message, character.name)
    chat_history_data = chat_history_instance.load(character, message.author.display_name)

    # 4) Load user settings (for temperature, max tokens, etc.)
    user_settings = settings.load_user_settings(message.author.id)
    prefix = user_settings.get("prefix", "").strip()

    # 5) Build the prompt
    prompt = build_prompt(
        chat_history=chat_history_data["messages"],
        user_display_name=message.author.display_name,
        message_content=message.content,
        character_name=character.name,
        prefix=prefix
    )

    # 6) Call the appropriate API
    if OPENAI_API_KEY:
        text_response = call_openai(context, prompt, user_settings, message.content)
    else:
        text_response = call_oobabooga(context, prompt, user_settings, message.author.display_name)

    # 7) Strip off the bot's name if it appears in the response
    character_prefix = f"{character.name}: "
    if text_response.startswith(character_prefix):
        text_response = text_response[len(character_prefix):].strip()

    # 8) Update character state using the last recorded state values from chat history
    previous_action = get_last_state_value(chat_history_data["messages"], "action", character.name)
    previous_appearance = get_last_state_value(chat_history_data["messages"], "appearance", character.name)
    previous_location = get_last_state_value(chat_history_data["messages"], "location", character.name)
    previous_mood = get_last_state_value(chat_history_data["messages"], "mood", character.name)

    # Map state keys to their previous values.
    state_prev = {
        "action": previous_action,
        "appearance": previous_appearance,
        "location": previous_location,
        "mood": previous_mood,
    }

    # Function to update a state, wrapping update_character_state.
    def update_state(state_key, prev_value):
        return update_character_state(
            character,
            state_key,
            prev_value,
            message.content,
            text_response,
            bool(OPENAI_API_KEY)
        )

    # Use a ThreadPoolExecutor to run the updates concurrently.
    state_results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a dictionary mapping futures to state keys.
        future_to_state = {
            executor.submit(update_state, state, prev_val): state
            for state, prev_val in state_prev.items()
        }
        for future in concurrent.futures.as_completed(future_to_state):
            state = future_to_state[future]
            try:
                state_results[state] = future.result()
            except Exception as exc:
                print(f"{state} generated an exception: {exc}")
                state_results[state] = state_prev[state]  # fallback to previous value

    # Now, assign the results to your variables.
    action = state_results["action"]
    appearance = state_results["appearance"]
    location = state_results["location"]
    mood = state_results["mood"]

    print("Character States:")
    print(f"  Action: {action}")
    print(f"  Appearance: {appearance}")
    print(f"  Location: {location}")
    print(f"  Mood: {mood}")

    # 9) Append new messages to chat history
    new_user_message = {
        "user": message.author.display_name,
        "message": message.content,
        "timestamp": message.created_at.isoformat()
    }
    new_bot_response = {
        "user": character.name,
        "message": text_response,
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "appearance": appearance,
        "location": location,
        "mood": mood
    }
    chat_history_data["messages"].extend([new_user_message, new_bot_response])

    # 10) Save updated chat history
    chat_history_instance.save(chat_history_data)

    # 11) Generate image prompt
    image_prompt = (
        f"{action}, {mood}, {character.species} {character.sex}, {character.hairstyle} {character.hair_color} hair, "
        f"{character.eye_color} eyes, {character.defining_features}, {appearance}, {location}"
    )

    return text_response, image_prompt
