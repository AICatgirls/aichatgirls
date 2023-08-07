# aichatgirls
Discord bot for [oobabooga webui](https://github.com/oobabooga/text-generation-webui)

This is my first project ever. Any suggestions or contributions are welcome!

## New Features

8/4/2023 - Added a `!remove <string>` command to remove a string from the bot's memory.

## Install
You will need to install oobabooga's [text-generation-webui](https://github.com/oobabooga/text-generation-webui)
 - `git clone https://github.com/AICatgirls/aichatgirls`
 - `pip install -r .\requirements.txt`
 You will need to create a discord bot and create an .env file with your bot's token in the format `TOKEN='your-token-here'`

You'll also need to modify the `start-webui.bat` file: `call python server.py --auto-devices --chat --wbits 4 --groupsize 128 --listen --model gpt4-x-alpaca-13b-native-4bit-128g --pre_layer 28 --extensions api --no-stream`
Replace the model with whichever model you are using, and if you have more than 8gb of VRAM the `--pre_layer 28` part can be removed so it will run faster
 
##  Character cards
Right now you have to rename your TavernAI character card to character.webp and place it into your aichatgirls folder.

## Starting
Start Oobabooga's text-generation-webui (start-webui.bat)
Start aichatgirls `python aichatgirls.py`

## Running
Messages you send to the discord bot will now be sent to oobabooga's text-generation-webui and answers returned
You can type `!help` in the discord chat to get a list of bot commands. Typing `!reset` will clear your history with the bod. Typing `!remove <string>` will remove the specified string from the bot's memory.

## Settings
Users can now alter the settings for                 
* max_response_length (max_new_tokens) - How long in tokens the response can be. Default 400
* temperature - A number between 0.1 and 1.9, default 0.5. The higher the number the more creative the response.
* repetition_penalty - A number between 0.1 and 1.9, default 1.18.
