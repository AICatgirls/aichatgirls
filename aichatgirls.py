# In chat mode the AI predicts future conversation, and we need to separate that from the immediate response
import discord
import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.ERROR)

# Set up Discord bot token and API endpoint URL
DISCORD_TOKEN = os.getenv('TOKEN')
API_ENDPOINT = "http://127.0.0.1:5000/api/v1/generate"

# Set up headers and payload for HTTP request
headers = {
    "Content-Type": "application/json"
}

# load a character card
with open('character.webp', 'rb') as f:
    webp_data = f.read()

# There's probably a better way to get the JSON from the character card
# Convert the binary data to a string
webp_string = webp_data.decode('ISO-8859-1')

# Extract the JSON string
start_index = webp_string.find('{"p')
end_index = webp_string.rfind('}') + 1
json_string = webp_string[start_index:end_index]

# Parse the JSON string to a Python object
metadata = json.loads(json_string)

# Access the properties
name = metadata['name']
description = metadata['description']
personality = metadata['personality']
first_mes = metadata['first_mes']
mes_example = metadata['mes_example']

# Initialize context with the initial conversation prompt
context = "Name: " + name + "\nDescription: " + description + "\nPersonality: " + personality

# Set up a list to keep track of chat history
chat_history = [mes_example, first_mes]

# Use Discord API wrapper library to send text response to Discord server
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print(message.content)
    # Ignore messages sent by the bot
    if message.author == client.user:
        return

    # Send the prompt to the API endpoint and get the response
    prompt = message.author.name + ": " + message.content + "\nFelicia: "
    prompt = context + ''.join(chat_history) + "\n" + prompt
    prompt = prompt[-2048:]    
    response = requests.post(API_ENDPOINT, headers=headers, json={"prompt": prompt})
    response_json = response.json()
    if len(response_json["results"]) > 0:
        text_response = response_json["results"][0]["text"]
    else:
        text_response = "Sorry, I couldn't generate a response."
    
    # Check for </p> or \n in text_response and truncate if found
    if "</p>" in text_response:
        text_response = text_response[:text_response.find("</p>")+4]
    if "\n" in text_response:
        text_response = text_response[:text_response.find("\n")]
    
    print(text_response)

    # Append the original message and text response to the chat history
    chat_history.append(message.content + "\nFelicia: ")
    chat_history.append(text_response)

    # Truncate the chat history to a maximum of 2048 characters
    if len(''.join(chat_history)) > 2048:
        chat_history.pop(0)

    # Send the text response back to the Discord server
    await message.channel.send(text_response)

client.run(DISCORD_TOKEN)
