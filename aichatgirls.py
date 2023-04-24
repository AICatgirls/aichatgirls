# In chat mode the AI predicts future conversation, and we need to separate that from the immediate response
import discord
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Set up Discord bot token and API endpoint URL
DISCORD_TOKEN = os.getenv('TOKEN')
API_ENDPOINT = "http://127.0.0.1:5000/api/v1/generate"

# Set up headers and payload for HTTP request
headers = {
    "Content-Type": "application/json"
}

# Initialize context with the initial conversation prompt
context = "Felicia is a woman who likes to wear cat ears to hold back her long light brown hair. She wears half-frame glasses, is very knowledgeable, loves to learn new things, and a bit flirty.\n\n" + \
          "Then the roleplay chat between You and Felicia begins.\n" + \
          "Felicia: Hi! I'm Felicia! What have you been up to lately?\n" + \
          "You: Hello!\n" + \
          "Felicia: Are you excited for the upcoming weekend? Any plans?\n" + \
          "You: Not really, I was thinking about going for a hike but it depends on the weather. How about you?\n" + \
          "Felicia: Oh, that sounds fun! I'm actually planning to attend a workshop on artificial intelligence. It should be quite enriching.\n" 

# Set up a list to keep track of chat history
chat_history = [context]

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
    if len(chat_history) > 0:
        prompt = chat_history[-1][-2048+len(prompt):] + "\n" + prompt
    response = requests.post(API_ENDPOINT, headers=headers, json={"prompt": prompt})
    response_json = response.json()
    print(response.json)
    text_response = response_json["results"][0]["text"] if len(response_json["results"]) > 0 else "Sorry, I couldn't generate a response."
    
    # Check for </p> or \n in text_response and truncate if found
    if "</p>" in text_response:
        text_response = text_response[:text_response.find("</p>")+4]
    if "\n" in text_response:
        text_response = text_response[:text_response.find("\n")]
    
    print(text_response)

    # Append the original message and text response to the chat history
    chat_history.append(message.content)
    chat_history.append(text_response)

    # Truncate the chat history to a maximum of 2048 characters
    if len(''.join(chat_history)) > 2048:
        chat_history.pop(0)

    # Send the text response back to the Discord server
    await message.channel.send(text_response)

client.run(DISCORD_TOKEN)
