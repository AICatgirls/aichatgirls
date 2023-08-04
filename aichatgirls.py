# TODO: try/except on requests, handle disconnects
# TODO: when the chat_history gets long oobabooga cuts off the context; make sure it gets preserved
import discord
import requests
import os
import asyncio
from datetime import datetime
import chatHistory
import chatCommand
from loadCharacterCard import load_character_card
from dotenv import load_dotenv
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
    print(message)
    if message.content:
        if message.content.startswith("!"):
            command = message.content.split(" ")[0]
            text_response = chatCommand.chat_command(command, message, character)
            if isinstance(message.channel, discord.DMChannel):
                await message.author.send(text_response)
            else:
                await message.channel.send(text_response)
        elif message.author == client.user:
            return
        else:
            chat_history = chatHistory.load_chat_history(message.author, character)

            # Send the prompt to the API endpoint and get the response
            prompt = (context + "\n" + chat_history[-MAX_CHAT_HISTORY_LENGTH:] + "\n" +
                f"{message.author.display_name}: {message.content}\n" +
                f"{character.name}: ")
            print(prompt)
            stopping_strings = [f"{message.author.display_name}:"]
            response = requests.post(
                API_ENDPOINT,
                headers=headers,
                json={
                    "prompt": prompt,
                    "max_length": 400,
                    "stopping_strings": stopping_strings
                }
            )
            
            # Keep checking if response has been received
            response_json = None
            while not response_json:
                # Show "typing" status while generating response
                async with message.channel.typing():
                    response_json = response.json()
                    if len(response_json["results"]) > 0:
                        text_response = response_json["results"][0]["text"]
                    else:
                        text_response = "Sorry, I couldn't generate a response."
                    await asyncio.sleep(1) # wait for 1 second before checking again

            # Append the original message and text response to the chat history
            chat_history += f"\n{message.author.name}: {message.content}\n{character.name}: {text_response}"
            chatHistory.save_chat_history(chat_history)

            if isinstance(message.channel, discord.DMChannel):
                await message.author.send(text_response)
            else:
                await message.channel.send(text_response)
    else:
        return
        
client.run(DISCORD_TOKEN)
