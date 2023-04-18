import discord
import websockets
import json
import os
from dotenv import load_dotenv
import hashlib
import string
import random

load_dotenv()
TOKEN = os.getenv('TOKEN')
GRADIO_FN = 29
client = discord.Client(intents=discord.Intents.default())

def random_hash():
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(9))

session = random_hash()

server = "127.0.0.1"
params = {
    'max_new_tokens': 200,
    'do_sample': True,
    'temperature': 0.5,
    'top_p': 0.9,
    'typical_p': 1,
    'repetition_penalty': 1.05,
    'encoder_repetition_penalty': 1.0,
    'top_k': 0,
    'min_length': 0,
    'no_repeat_ngram_size': 0,
    'num_beams': 1,
    'penalty_alpha': 0,
    'length_penalty': 1,
    'early_stopping': False,
    'seed': -1,
    'add_bos_token': True,
    'truncation_length': 2048,
    'custom_stopping_strings': [],
    'ban_eos_token': False
}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    print(f'received message {message.content}')
    if message.author == client.user:
        return

    if message.content.startswith('$connect'):
        # Update the payload with the new message content
        payload = json.dumps([message.content, params])
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
