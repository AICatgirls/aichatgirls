import os
from cryptography.fernet import Fernet, InvalidToken
import discord
from dotenv import load_dotenv
from encryption import get_or_generate_key

load_dotenv()

class ChatHistory:
    def __init__(self, message, bot_name):
        if isinstance(message.channel, discord.DMChannel):
            self.filename = f"{message.author}-{bot_name}.txt"
        else:
            self.filename = f"{message.channel.guild}-{message.channel}-{message.channel.id}.txt"
        self.cipher_suite = self.get_or_generate_cipher_suite()

    def get_or_generate_cipher_suite(self):
        encryption_key = get_or_generate_key()
        return Fernet(encryption_key)
            
    def load(self, character):
        if os.path.isfile(self.filename):
            with open(self.filename, "rb") as f:
                encrypted_data = f.read()
                try:
                    decrypted_data = self.decrypt(encrypted_data)
                except InvalidToken:
                    # Decryption failed, consider the file plaintext
                    decrypted_data = encrypted_data.decode("utf-8")
        else:
            decrypted_data = character.first_mes + character.mes_example

        return decrypted_data

    def save(self, data):
        encrypted_data = self.encrypt(data)
        with open(self.filename, "wb") as f:
            f.write(encrypted_data)

    def reset(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def encrypt(self, data):
        encrypted_data = self.cipher_suite.encrypt(data.encode("utf-8"))
        return encrypted_data

    def decrypt(self, encrypted_data):
        decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode("utf-8")
        return decrypted_data
