# aichatgirls
Discord bot for [oobabooga webui](https://github.com/oobabooga/text-generation-webui)

This is my first project ever. Any suggestions or contributions are welcome!

## Install
You will need to install oobabooga's [text-generation-webui](https://github.com/oobabooga/text-generation-webui)
 - `git clone https://github.com/AICatgirls/aichatgirls`
 - `pip install -r .\requirements.txt`
 You will need to create a discord bot and create an .env file with your bot's token in the format `TOKEN='your-token-here'`

You'll also need to modify the `start-webui.bat` file: `call python server.py --auto-devices --chat --wbits 4 --groupsize 128 --listen --model TheBloke_Wizard-Vicuna-13B-Uncensored-SuperHOT-8K-GPTQ --gpu-split 4,8 --extensions api --no-stream --loader ExLlama --max_seq_len 8192 --compress_pos_emb 4`
Replace the model with whichever model you are using, and the --gpu-split to match whatever hardware you are using (remove if only using one GPU).
 
##  Character cards
Right now you have to rename your TavernAI character card to character.webp and place it into your aichatgirls folder.

## Starting
Start Oobabooga's text-generation-webui (start-webui.bat)
Start aichatgirls `python aichatgirls.py`

## Running
Messages you send to the discord bot will now be sent to oobabooga's text-generation-webui and answers returned
You can type `!help` in the discord chat to get a list of bot commands. Typing `!reset` will clear your history with the bod.
