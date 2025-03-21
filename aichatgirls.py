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
import discord
from datetime import datetime
import encryption
from chatCommand import chat_command
from generate import generate_prompt_response
from imagegen import generate_animation_gif_async
from io import BytesIO
import loadCharacterCard
from scripts.whitelist import Whitelist
import threading

DISCORD_TOKEN = os.getenv('TOKEN')
ALLOW_DMS = os.getenv('ALLOW_DMS', 'true').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = discord.Client(intents=discord.Intents.all())
whitelist = Whitelist()

# For local console chat
USER_NAME = "localuser"

async def console_chat():
    print("Local chat enabled. Type 'exit' to stop console chat.")
    while True:
        user_input = await asyncio.to_thread(input)  # Non-blocking input in an async function
        user_input = user_input.strip()

        if user_input.lower() == "exit":
            print("Console chat disabled.")
            break

        # Create a mock message object with minimal attributes
        message_mock = type('', (), {})()
        # Make sure we assign an 'id' to the author—this is used by generate.py to load user-specific data
        message_mock.author = type('', (), {
            "display_name": USER_NAME,
            "id": 1234567890,  # Just a dummy ID for local user
            "__str__": lambda self: USER_NAME
        })()
        message_mock.content = user_input
        message_mock.created_at = datetime.now()
        message_mock.channel = type('', (), {
            "guild": USER_NAME,
            "name": "local_chat",
            "id": 0,
            "__str__": lambda self: "local_chat"
        })()

        character = loadCharacterCard.Character.load_character_card(message_mock.author.id, "Felicia", use_openai=bool(OPENAI_API_KEY))

        # Slash commands still check before generating a response
        if user_input.startswith("/"):
            response = chat_command(user_input, message_mock, character)
        else:
            # Use the new generate function, which handles character loading internally
            response = await generate_prompt_response(message_mock)
        
        # Print the response to the console
        print(f"Bot: {response}")

async def start_console_chat():
    asyncio.create_task(console_chat())  # Run as a background task

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    encryption.get_or_generate_key()   
    asyncio.create_task(start_console_chat())

@client.event
async def on_message(message):
    # Ignore our own messages
    if message.author == client.user:
        return

    # If there's no content, do nothing
    if not message.content:
        return

    # Check DM allowance
    if not ALLOW_DMS and isinstance(message.channel, discord.DMChannel):
        return

    image_prompt = None

    # Slash commands first
    if message.content.startswith("/"):
        command = message.content.split(" ")[0]
        character = loadCharacterCard.Character.load_character_card(message.author.id, client.user.name, use_openai=bool(OPENAI_API_KEY))
        text_response = chat_command(command, message, character)
    else:
        # Only process if channel is whitelisted
        if not whitelist.is_channel_whitelisted(message.channel):
            return
        # Generate a text response and an image prompt
        text_response, image_prompt = await generate_prompt_response(message)



    # If response is longer than 2000 characters, split and send multiple messages
    chunks = [text_response[i:i + 2000] for i in range(0, len(text_response), 2000)]
    sender = message.author.send if isinstance(message.channel, discord.DMChannel) else message.channel.send

    if image_prompt:
        print(f"Generating image for: {image_prompt}")
        try:
            gif_bytes = await generate_animation_gif_async(image_prompt)
            if chunks:
                # Send the first chunk with the image attached.
                await sender(content=chunks[0],
                             file=discord.File(BytesIO(gif_bytes), filename='generated_animation.gif'))
                # Send any additional chunks separately.
                for chunk in chunks[1:]:
                    await sender(chunk)
            else:
                # If there's no text, just send the image.
                await sender(file=discord.File(BytesIO(gif_bytes), filename='generated_animation.gif'))
        except Exception as e:
            # If image generation fails, send all text chunks and the error message.
            for chunk in chunks:
                await sender(chunk)
            await sender(f"Error generating image: {e}")
    else:
        # If no image prompt, just send all text chunks.
        for chunk in chunks:
            await sender(chunk)

if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
else:
    print("Discord integration disabled. Running local chat only.")

    # Just run local console chat
    asyncio.run(console_chat())
