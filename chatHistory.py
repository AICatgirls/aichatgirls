import os
import json
from cryptography.fernet import Fernet, InvalidToken
import discord
from dotenv import load_dotenv
from encryption import get_or_generate_key

load_dotenv()

class ChatHistory:
    def __init__(self, message, bot_name):
        if isinstance(message.channel, discord.DMChannel):
            self.filename = f"{message.author.id}-{bot_name}.json"
        else:
            self.filename = f"{message.channel.guild.id}-{message.channel.id}-{bot_name}.json"
        self.cipher_suite = self.get_or_generate_cipher_suite()

    def get_or_generate_cipher_suite(self):
        encryption_key = get_or_generate_key()
        return Fernet(encryption_key)

    def load(self, character, user):
        if os.path.isfile(self.filename):
            with open(self.filename, "rb") as f:
                encrypted_data = f.read()
                try:
                    decrypted_data = self.decrypt(encrypted_data)
                    # Attempt to parse JSON
                    try:
                        return json.loads(decrypted_data)
                    except json.JSONDecodeError:
                        # If not JSON, convert existing text data to JSON format
                        return self.convert_to_json(decrypted_data, character, user)
                except InvalidToken:
                    # Decryption failed, treat as plain text and convert
                    decrypted_data = encrypted_data.decode("utf-8")
                    return self.convert_to_json(decrypted_data, character, user)
        else:
            # Create new JSON structure if no file exists
            return {"header": {"file_format_version": "1.0"}, "messages": []}

    def save(self, data):
        json_data = json.dumps(data, indent=4)
        encrypted_data = self.encrypt(json_data)
        with open(self.filename, "wb") as f:
            f.write(encrypted_data)

    def reset(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def encrypt(self, data):
        return self.cipher_suite.encrypt(data.encode("utf-8"))

    def decrypt(self, encrypted_data):
        return self.cipher_suite.decrypt(encrypted_data).decode("utf-8")

    def convert_to_json(self, txt_data, character, user):
        # Convert existing plain text chat history to JSON
        # This method needs to be implemented based on your existing .txt format
        # Example: Splitting the txt_data into messages and converting them into JSON objects
        messages = txt_data.split('\n')  # Example split, adjust based on your format
        json_messages = [{"message": msg, "user": user} for msg in messages]  # Example conversion
        return {"header": {"file_format_version": "1.0"}, "messages": json_messages}