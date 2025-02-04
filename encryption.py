from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

def get_or_generate_key():
    encryption_key = os.getenv('SECRET_KEY')
    if encryption_key:
        return encryption_key
    else:
        generated_key = Fernet.generate_key()
        save_key_to_dotenv(generated_key)
        return generated_key

def save_key_to_dotenv(key):
    with open('.env', 'a') as f:
        f.write(f"\nSECRET_KEY={key.decode()}\n")

# Call get_or_generate_key when this module is imported to ensure key presence
get_or_generate_key()
