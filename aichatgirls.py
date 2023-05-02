# TODO: show when the bot is "typing"
# TODO: add "reset" command to clear chat history
# TODO: try/except on requests, handle disconnects
# TODO: when the chat_history gets long oobabooga cuts off the context; make sure it gets preserved
import discord
import requests
import os
from datetime import datetime
import chatHistory
from loadCharacterCard import load_character_card
from dotenv import load_dotenv
load_dotenv()

MODEL_MAX_TOKENS = 2048
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

# Check if discord token TOKEN is set in .env file
if not os.getenv('TOKEN'):
    print("Error: You need to create a .env file with TOKEN='your-discord-token' or the bot will not work")
    exit(1)

# Set up Discord bot token and API endpoint URL
DISCORD_TOKEN = os.getenv('TOKEN')
API_ENDPOINT = "http://127.0.0.1:5000/api/v1/generate"
client = discord.Client(intents=discord.Intents.default())

# Set up headers and payload for HTTP request
headers = {
    "Content-Type": "application/json"
}

character = {}
context = ""

@client.event
async def on_ready():
    global character
    global context
    print('Logged in as {0.user}'.format(client))
    character = load_character_card(client.user.name)
    context = f"Name: {character.name}\nDescription: {character.description}\nPersonality: {character.personality}\n"
    print(context)

@client.event
async def on_message(message):
    print(message.author)
    print(message.content)
    chat_history = chatHistory.load_chat_history(message.author, character.name)
    if chat_history == "":
        chat_history = character.mes_example + character.first_mes
    
    # Ignore messages sent by the bot
    if message.author == client.user:
        return

    # Send the prompt to the API endpoint and get the response
    prompt = f"{message.author.display_name}: {message.content}\n{character.name}: "
    prompt = context + chat_history[-MAX_CHAT_HISTORY_LENGTH:] + "\n" + prompt
    response = requests.post(
        API_ENDPOINT,
        headers=headers,
        json={
            "prompt": prompt,
            "max_length": 200,
            "repetition_penalty": 1.2,
            "stopping_strings": ["\n","</p>"]
        }
    )
    response_json = response.json()
    print(response_json['results'])
    if len(response_json["results"]) > 0:
        text_response = response_json["results"][0]["text"]
    else:
        text_response = "Sorry, I couldn't generate a response."

    # Append the original message and text response to the chat history
    chat_history += f"\n{message.author.name}: {message.content}\n{character.name}: {text_response}"
    chatHistory.save_chat_history(chat_history)
    
    await message.channel.send(text_response)

client.run(DISCORD_TOKEN)
