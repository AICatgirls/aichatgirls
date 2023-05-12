import os

CHAT_HISTORY_FILENAME = ""

def set_chat_history_filename(author, bot_name):
    global CHAT_HISTORY_FILENAME
    CHAT_HISTORY_FILENAME = str(author) + "-" + str(bot_name) + ".txt"

def load_chat_history(author, character):
    set_chat_history_filename(author, character.name)
    if os.path.isfile(CHAT_HISTORY_FILENAME):
        with open(CHAT_HISTORY_FILENAME, "r", encoding="utf-8") as f:
            chat_history = f.read()
    else:
        chat_history = ""
        
    if chat_history == "":
        chat_history = character.mes_example + character.first_mes
        
    return chat_history

def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILENAME, "w", encoding="utf-8") as f:
        f.write(chat_history)
        
def reset_chat_history(author, bot_name):
    set_chat_history_filename(author, bot_name)
    if os.path.isfile(CHAT_HISTORY_FILENAME):
        os.remove(CHAT_HISTORY_FILENAME)