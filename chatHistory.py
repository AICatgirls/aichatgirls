import os

CHAT_HISTORY_FILENAME = ""

def set_chat_history_filename(author):
    global CHAT_HISTORY_FILENAME
    CHAT_HISTORY_FILENAME = str(author) + ".txt"

def load_chat_history(author):
    chat_history = ""
    set_chat_history_filename(author)
    if os.path.isfile(CHAT_HISTORY_FILENAME):
        with open(CHAT_HISTORY_FILENAME, "r") as f:
            chat_history = f.read()
    return chat_history

def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILENAME, "w") as f:
        f.write(chat_history)