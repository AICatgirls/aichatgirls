# TODO: try/except on requests, handle disconnects
# TODO: Tokenize user messages to get an exact count of tokens rather than estimating it based on length
#       Check the API documentation in textgen, there's an endpoint for token stuff. We also get this in responses now too I think.
# TODO: Command ideas: regen, undo
# TODO: Scheduled messages
# TODO: Group chat mode where history is shared by the channel
# TODO: Image generator/image interpreter
# TODO: Delete DM history
# TODO: Text to speech

# Check if discord token TOKEN is set in .env file
from dotenv import load_dotenv
import os
load_dotenv()
if not os.getenv('TOKEN'):
    print("NOTICE: To use this with discord, you need to create a .env file with TOKEN='your-discord-token' (in single quotes)")
# ChatGPT doesn't like reading the above, so I've moved it to the top to make it easier to exclude it

import asyncio
from chatCommand import chat_command
from datetime import datetime
import discord
import encryption
from generate import generate_prompt_response
import loadCharacterCard
from scripts.whitelist import Whitelist
import threading

DISCORD_TOKEN = os.getenv('TOKEN')
ALLOW_DMS = os.getenv('ALLOW_DMS', 'true').lower() == 'true'
client = discord.Client(intents=discord.Intents.all())
whitelist = Whitelist()

character = {}
context = ""
USER_NAME = "localuser"

async def console_chat():
    print("Local chat enabled. Type 'exit' to stop console chat.")
    while True:
        user_input = await asyncio.to_thread(input)  # Non-blocking input in an async function
        user_input = user_input.strip()

        if user_input.lower() == "exit":
            print("Console chat disabled.")
            break

        message_mock = type('', (), {})()
        message_mock.author = type('', (), {"display_name": USER_NAME, "__str__": lambda self: USER_NAME})()
        message_mock.content = user_input
        message_mock.created_at = datetime.now()
        message_mock.channel = type('', (), {
            "guild": USER_NAME,
            "name": "local_chat",
            "id": 0,
            "__str__": lambda self: "local_chat"
        })()

        # Check for slash commands before sending to generate_prompt_response
        if user_input.startswith("/"):
            response = chat_command(user_input, message_mock, character)
            print(f"DEBUG: chat_command response for '{user_input}': {response}")
        else:
            response = await generate_prompt_response(message_mock, character, context)
            
        print(f"{character.name}: {response}")

async def start_console_chat():
    asyncio.create_task(console_chat())  # Run as a background task

@client.event
async def on_ready():
    global character
    global context
    print('Logged in as {0.user}'.format(client))
    character = loadCharacterCard.Character.load_character_card(client.user.name)
    context = f"Name: {character.name}\nDescription: {character.description}\nPersonality: {character.personality}"
    encryption.get_or_generate_key()
    asyncio.create_task(start_console_chat())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content:
        if not ALLOW_DMS and isinstance(message.channel, discord.DMChannel):
            return
        if message.content.startswith("/"): # slash commands process first
            command = message.content.split(" ")[0]
            text_response = chat_command(command, message, character)
        else:
            if not whitelist.is_channel_whitelisted(message.channel):
                return
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
