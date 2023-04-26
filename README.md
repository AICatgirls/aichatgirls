# aichatgirls
Discord bot for [oobabooga webui](https://github.com/oobabooga/text-generation-webui)

This is my first project ever. Any suggestions or contributions are welcome!

## Install
You will need to install oobabooga's [text-generation-webui](https://github.com/oobabooga/text-generation-webui)
 - `git clone https://github.com/AICatgirls/aichatgirls`
 - `pip install -r .\requirements.txt`
 You will also need to create a discord bot and create an .env file with your bot's token in the format `TOKEN='your-token-here'`
 
Oobabooga has a broken API at the moment. If you git cloned their repo try this command: `git reset --hard 7ff645899e4610b16574bdd22a4d154c93d5b830` to revert to a working version.

You'll also need to modify the `start-webui.bat` file: `call python server.py --auto-devices --chat --wbits 4 --groupsize 128 --listen --model gpt4-x-alpaca-13b-native-4bit-128g --pre_layer 28 --extensions api`
Replace the model with whichever model you are using, and if you have more than 8gb of VRAM the `--pre_layer 28` part can be removed so it will run faster
 
##  Character cards
Right now you have to rename your TavernAI character card to character.webp and place it into your aichatgirls folder.

## Starting
Start Oobabooga's text-generation-webui (start-webui.bat)
Start aichatgirls `python aichatgirls.py`

## Running
Messages you send to the discord bot will now be sent to oobabooga's text-generation-webui and answers returned
