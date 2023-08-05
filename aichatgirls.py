# TODO: try/except on requests, handle disconnects
# TODO: Allow user configurable max response length,
#       Send multiple messages if it exceeds discord's 2000 character length
# TODO: Make temperature a user configurable setting
# TODO: Tokenize user messages to get an exact count of tokens rather than estimating it based on length
# TODO: Command ideas: regen, undo

import chatCommand
from datetime import datetime
import discord
from dotenv import load_dotenv
from generate import generate_prompt_response
from loadCharacterCard import load_character_card
import os
import requests

load_dotenv()

MODEL_MAX_TOKENS = 8000
AVERAGE_CHARACTERS_PER_TOKEN = 3.525
MAX_CHAT_HISTORY_LENGTH = int(MODEL_MAX_TOKENS * AVERAGE_CHARACTERS_PER_TOKEN * 0.9)

# Check if discord token TOKEN is set in .env file
if not os.getenv('TOKEN'):
    print("Error: You need to create a .env file with TOKEN='your-discord-token' or the bot will not work")
    exit(1)

# Set up Discord bot token and API endpoint URL
DISCORD_TOKEN = os.getenv('TOKEN')
API_ENDPOINT = "http://127.0.0.1:5000/api/v1/generate"
client = discord.Client(intents=discord.Intents.all())

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
    if message.author == client.user:
        return
    print(message)
    if message.content:
        if message.content.startswith("!"):
            command = message.content.split(" ")[0]
            text_response = await handle_command(command, message)
        else:
            text_response = await generate_prompt_response(message, API_ENDPOINT, headers, character, context, MAX_CHAT_HISTORY_LENGTH)

        if isinstance(message.channel, discord.DMChannel):
            await message.author.send(text_response)
        else:
            await message.channel.send(text_response)

    else:
        return

async def handle_command(command, message):
    return chatCommand.chat_command(command, message, character)
        
client.run(DISCORD_TOKEN)
