# TODO: try/except on requests, handle disconnects
# TODO: Allow user configurable max response length,
#       Send multiple messages if it exceeds discord's 2000 character length
# TODO: Make temperature a user configurable setting
# TODO: Tokenize user messages to get an exact count of tokens rather than estimating it based on length
# TODO: Command ideas: regen, undo


# Check if discord token TOKEN is set in .env file
from dotenv import load_dotenv
import os
load_dotenv()
if not os.getenv('TOKEN'):
    print("Error: You need to create a .env file with TOKEN='your-discord-token' or the bot will not work")
    exit(1)
# ChatGPT doesn't like reading the above, so I've moved it to the top to make it easier to exclude it

from chatCommand import chat_command
from datetime import datetime
import discord
import encryption
from generate import generate_prompt_response
import loadCharacterCard
import requests

# Set up Discord bot token and API endpoint URL
DISCORD_TOKEN = os.getenv('TOKEN')
client = discord.Client(intents=discord.Intents.all())

character = {}
context = ""

@client.event
async def on_ready():
    global character
    global context
    print('Logged in as {0.user}'.format(client))
    character = loadCharacterCard.load_character_card(client.user.name)
    context = f"Name: {character.name}\nDescription: {character.description}\nPersonality: {character.personality}\n"
    encryption.get_or_generate_key()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message)
    if message.content:
        if message.content.startswith("!"):
            command = message.content.split(" ")[0]
            text_response = chat_command(command, message, character)
        else:
            text_response = await generate_prompt_response(message, character, context)

        # If response is longer than 2000 characters, split and send multiple messages
        chunks = [text_response[i:i + 2000] for i in range(0, len(text_response), 2000)]
        for chunk in chunks:
            if isinstance(message.channel, discord.DMChannel):
                await message.author.send(chunk)
            else:
                await message.channel.send(chunk)

    else:
        return
        
client.run(DISCORD_TOKEN)
