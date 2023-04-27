import os

CHAT_HISTORY_FILENAME = ""

def set_chat_history_filename(author, bot):
    global CHAT_HISTORY_FILENAME
    CHAT_HISTORY_FILENAME = str(author) + "-" + str(bot) + ".txt"

def load_chat_history(author, bot):
    chat_history = ""
    set_chat_history_filename(author, bot)
    if os.path.isfile(CHAT_HISTORY_FILENAME):
        with open(CHAT_HISTORY_FILENAME, "r", encoding="utf-8") as f:
            chat_history = f.read()
    return chat_history

def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILENAME, "w", encoding="utf-8") as f:
        f.write(chat_history)