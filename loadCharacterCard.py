import json

class Character:
    def __init__(self, name, description, personality, first_mes, mes_example):
        self.name = name
        self.description = description
        self.personality = personality
        self.first_mes = first_mes
        self.mes_example = mes_example

def load_character_card(username=""):
    try:
        # load a character card
        with open('character.webp', 'rb') as f:
            webp_data = f.read()

        # There's probably a better way to get the JSON from the character card
        # Convert the binary data to a string
        webp_string = webp_data.decode('ISO-8859-1')

        # Extract the JSON string
        start_index = webp_string.find('{"p')
        end_index = webp_string.rfind('}') + 1
        json_string = webp_string[start_index:end_index]

        # Parse the JSON string to a Python object
        metadata = json.loads(json_string)

        # Access the properties
        name = metadata['name']
        description = metadata['description']
        personality = metadata['personality']
        first_mes = metadata['first_mes']
        mes_example = metadata['mes_example']

    except (FileNotFoundError, KeyError):
        # Use the default character if there's no character card or if we can't load properties from it
        name = username
        description = f"{username} is a 32 year old woman wearing cat ears, half-rim glasses, purple crop top, purple pleated skirt, fishnet stockings, platform boots, and a collar. She has light brown hair, green eyes, and a light blue Manchester City FC scarf. {username} loves to ask questions and learn new things. {username} has a great sense of humor and will laugh and tell jokes. {username} has a bachelor's degree in economics from The Evergreen State College. She owns a small chain of coffee shops. {username} is lonely and really likes it when people spend time talking to her. {username} loves to give praise, and looks for ways she can give compliments."
        personality = "intelligent, tipsy, flirty, entrepreneurial, bubbly"
        first_mes = f"{username}: Hi! My name is {username} and it is absolutely my pleasure to meet you. Oh my gosh you are so stunning!"
        mes_example = f"{username}: I love how every time I see you you're smiling. You brighten my day! What can I do for you?\n{{user}}: I just came by to see how you were doing\n{username}: It's a lovely day and I'm feeling bonita! Thank you for thinking of me!\n{{user}}: Also I just like talking with you\n{username}: *blushes* I appreciate every moment I get with you. How are you doing? Did you have anything to eat today?"

    return Character(name, description, personality, first_mes, mes_example)
