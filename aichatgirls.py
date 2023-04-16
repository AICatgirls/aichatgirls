import discord
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    print(f'received message {message.content}')
    if message.author == client.user:
        return

    if message.content.startswith('$connect'):
        server = 'localhost' # replace with your server address
        async with websockets.connect(f'ws://{server}:7860/queue/join') as websocket:
            while content := json.loads(await websocket.recv()):
                match content['msg']:
                    case 'send_hash':
                        await websocket.send(json.dumps({
                            'session_hash': session,
                            'fn_index': GRADIO_FN
                        }))
                    case 'estimation':
                        pass
                    case 'send_data':
                        await websocket.send(json.dumps({
                            'session_hash': session,
                            'fn_index': GRADIO_FN,
                            'data': [payload]
                        }))
                    case 'process_starts':
                        pass
                    case 'process_generating' | 'process_completed':
                        return content['output']['data'][0]
                        if content['msg'] == 'process_completed':
                            break

client.run(TOKEN)