import os
import json
from cryptography.fernet import Fernet, InvalidToken
import discord
from dotenv import load_dotenv
from encryption import get_or_generate_key

load_dotenv()

class ChatHistory:
    def __init__(self, message, bot_name):
        self.filename = self.determine_filename(message, bot_name)
        self.cipher_suite = self.get_or_generate_cipher_suite()

    def determine_filename(self, message, bot_name):
        if isinstance(message.channel, discord.DMChannel):
            return f"{message.author}-{bot_name}.txt"
        else:
            return f"{message.channel.guild}-{message.channel}-{message.channel.id}.txt"

    def get_or_generate_cipher_suite(self):
        encryption_key = get_or_generate_key()
        return Fernet(encryption_key)

    def load(self, character, user):
        if os.path.isfile(self.filename):
            decrypted_data = self.read_and_decrypt()
            return self.parse_chat_history(decrypted_data, character, user)
        else:
            return self.initialize_new_history(character, user)

    def save(self, data):
        encrypted_data = self.encrypt(json.dumps(data, indent=4))
        with open(self.filename, "wb") as f:
            f.write(encrypted_data)

    def reset(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def read_and_decrypt(self):
        with open(self.filename, "rb") as f:
            encrypted_data = f.read()
            try:
                return self.decrypt(encrypted_data)
            except InvalidToken:
                # Handle decryption failure if necessary
                return encrypted_data.decode("utf-8")

    def parse_chat_history(self, data, character, user):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return self.convert_to_json(data, character, user)

    def initialize_new_history(self, character, user):
        formatted_mes_example = character.mes_example.replace("{user}", f"{user}")
        formatted_first_mes = character.first_mes
        combined_default_messages = f"{formatted_mes_example}\n{formatted_first_mes}"

        # Use convert_to_json to create the initial chat history
        return self.convert_to_json(combined_default_messages, character, user)

    def encrypt(self, data):
        return self.cipher_suite.encrypt(data.encode("utf-8"))

    def decrypt(self, encrypted_data):
        return self.cipher_suite.decrypt(encrypted_data).decode("utf-8")

    def convert_to_json(self, txt_data, character, user):
        lines = txt_data.split('\n')
        json_messages = []

        for line in lines:
            if line.strip():
                # Splitting each line into 'user' and 'message'
                if ": " in line:
                    line_user, message = line.split(": ", 1)
                    json_messages.append({"user": line_user, "message": message})
                else:
                    # Handling lines that don't follow the expected format
                    json_messages.append({"user": "Unknown", "message": line})

        return {"header": {"file_format_version": "1.0"}, "messages": json_messages}