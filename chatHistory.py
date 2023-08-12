import os
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
from encryption import get_or_generate_key

load_dotenv()

class EncryptedChatHistory:
    def __init__(self, author, bot_name):
        self.filename = f"{author}-{bot_name}.txt"
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
            decrypted_data = character.mes_example + character.first_mes

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
