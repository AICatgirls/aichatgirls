# aichatgirls
Discord bot for [oobabooga webui](https://github.com/oobabooga/text-generation-webui)

This is my first project ever. Any suggestions or contributions are welcome!

## New Features

8/7/2023 - Bots can now produce discord messages longer than 2000 characters by splitting the response into multiple messages

8/4/2023 - Added a `!remove <string>` command to remove a string from the bot's memory.

## Install
1. `git clone https://github.com/AICatgirls/aichatgirls.git`
2. In the aichatgirls folder (`cd aichatgirls`), run `pip install -4 .\requirements.txt`
3. You will need to create a discord bot
4. Create a file named `.env` in notepad and write one line with your bot's discord token in the format `TOKEN='your-token-here'`
5. Install oobabooga's [text-generation-webui](https://github.com/oobabooga/text-generation-webui). Make sure to add `--api` to the CMD_FLAGS.txt file.

I more or less use the Vicuna template for this chatbot. TheBloke/Wizard-Vicuna-13B-Uncensored-SuperHOT-8K-fp16 seems to work pretty well.
 
##  Character cards
Right now you have to rename your TavernAI character card to character.webp and place it into your aichatgirls folder. If you're using character cards I would love to have your feedback!

## Starting
Start Oobabooga's text-generation-webui (start-webui.bat)
Start aichatgirls `python aichatgirls.py`

## Running
Messages you send to the discord bot will now be sent to oobabooga's text-generation-webui and answers returned
You can type `!help` in the discord chat to get a list of bot commands. Typing `!reset` will clear your history with the bod. Typing `!remove <string>` will remove the specified string from the bot's memory.

## Settings
Users can now alter the settings for                 
* max_response_length (max_new_tokens) - How long in tokens the response can be. Default 400
* min_length - How long you want the responses to be. Default 0
* temperature - A number between 0.1 and 1.9, default 0.5. The higher the number the more creative the response.
* repetition_penalty - A number between 0.1 and 1.9, default 1.18.
* prefix - A hidden phrase that the bot will silently say before giving a response. Default none.