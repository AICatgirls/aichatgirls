import requests
import chatHistory
import asyncio

async def generate_prompt_response(message, API_ENDPOINT, headers, character, context, MAX_CHAT_HISTORY_LENGTH):
    chat_history = chatHistory.load_chat_history(message.author, character)
    prompt = (context + "\n" + chat_history[-MAX_CHAT_HISTORY_LENGTH:] + "\n" +
              f"{message.author.display_name}: {message.content}\n" +
              f"{character.name}: ")
    response = requests.post(
        API_ENDPOINT,
        headers=headers,
        json={
            "prompt": prompt,
            "max_new_tokens": 400,
            "temperature": 0.5,
            "repetition_penalty": 1.18,
            "stopping_strings": [f"{message.author.display_name}:"]
        }
    )
    
    response_json = None
    while not response_json:
        response_json = response.json()
        if len(response_json["results"]) > 0:
            text_response = response_json["results"][0]["text"]
        else:
            text_response = "Sorry, I couldn't generate a response."
        await asyncio.sleep(1)  # wait for 1 second before checking again
        
    # Append the original message and text response to the chat history
    chat_history += f"\n{message.author.name}: {message.content}\n{character.name}: {text_response}"
    chatHistory.save_chat_history(chat_history)

    return text_response
