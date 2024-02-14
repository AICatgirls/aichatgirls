# aichatgirls
Discord bot for [oobabooga webui](https://github.com/oobabooga/text-generation-webui)

This is my first project ever. Any suggestions or contributions are welcome!

## New Features
2/13/2024 - You can add `ALLOW_DMS=false` to the `.env` file to make the bot ignore DMs

8/11/2023 - Chat history is now encrypted. ChatCommands now start with / instead of !.

8/7/2023 - Bots can now produce discord messages longer than 2000 characters by splitting the response into multiple messages

8/4/2023 - Added a `/remove <string>` command to remove a string from the bot's memory.

## Install
1. `git clone https://github.com/AICatgirls/aichatgirls.git`
2. In the aichatgirls folder (`cd aichatgirls`), run `pip install -r .\requirements.txt`
3. You will need to create a discord bot
4. Create a file named `.env` in notepad and write one line with your bot's discord token in the format `TOKEN='your-token-here'`
5. Install oobabooga's [text-generation-webui](https://github.com/oobabooga/text-generation-webui). Make sure to add `--api` to the CMD_FLAGS.txt file.

Text-generation-webui should automatically set the template for your model when you load it. I use TheBloke/Wizard-Vicuna-13B-Uncensored-SuperHOT-8K-fp16 though I'm sure there are better models available these days.
 
##  Character cards
Right now you have to rename your TavernAI character card to character.webp and place it into your aichatgirls folder. If you're using character cards I would love to have your feedback!

## Starting
- Start Oobabooga's text-generation-webui (`start-windows.bat`, `start-linux.sh`, `start_macos.sh`, or `start_wsl.bat` depending on your OS)
- Start aichatgirls `python aichatgirls.py`

## Running
Messages you send to the discord bot will now be sent to oobabooga's text-generation-webui and answers returned. To use the bot in a chat channel make sure it has permission and type `/whitelist`.

You can type `/help` in the discord chat to get a list of bot commands, and `/set` to get a list of settings.

## Settings
Users can now alter bot settings. Usage `/set [setting] [value]` or `/set [setting]` to reset a setting to default
* max_response_length (max_new_tokens) - How long in tokens the response can be. Default 400
* min_length - How long you want the responses to be. Default 0
* temperature - A number between 0.1 and 1.9, default 0.4. The higher the number the more creative the response.
* repetition_penalty - A number between 0.1 and 1.9, default 1.18.
* prefix - A hidden phrase that the bot will silently say before giving a response. Default none.
