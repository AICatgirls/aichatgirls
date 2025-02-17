import re
from typing import Optional
from settings import load_user_settings


class Character:
    def __init__(self, name, description, personality, first_mes, mes_example):
        self.name = name
        self.description = description
        self.personality = personality
        self.first_mes = first_mes
        self.mes_example = mes_example

    @staticmethod
    def extract_property(webp_data: bytes, property_name: str) -> Optional[str]:
        """
        Extracts the value of a given property_name in the format:
            property_name: "<value>"
        Returns None if not found.
        """
        pattern = rb'%s: "(.*?)(?<!\\)"' % property_name.encode()
        match = re.search(pattern, webp_data)
        return match.group(1).decode('utf-8') if match else None

    @classmethod
    def read_character_card_data(cls) -> Optional[dict]:
        """
        Attempts to read data from 'character.webp' and extract properties.
        Returns a dict of properties if successful, or None if any property is missing or invalid.
        """
        try:
            with open('character.webp', 'rb') as f:
                webp_data = f.read()

            # Extract each property
            name = cls.extract_property(webp_data, 'name')
            description = cls.extract_property(webp_data, 'description')
            personality = cls.extract_property(webp_data, 'personality')
            first_mes = cls.extract_property(webp_data, 'first_mes')
            mes_example = cls.extract_property(webp_data, 'mes_example')

            # If any property is missing, treat the card as invalid
            if any(prop is None for prop in [name, description, personality, first_mes, mes_example]):
                raise ValueError("One or more properties not found in character.webp")

            return {
                "name": name,
                "description": description,
                "personality": personality,
                "first_mes": first_mes,
                "mes_example": mes_example,
            }

        except (FileNotFoundError, KeyError, ValueError) as e:
            print(f"Error reading character.webp: {e}")
            return None

    @staticmethod
    def is_valid_value(value: Optional[str]) -> bool:
        """
        Checks whether a given value is non-empty and not None.
        Adjust this to your own validation needs.
        """
        return bool(value and value.strip())

    @classmethod
    def load_character_card(cls, user_id: str, fallback_name: str = "Felicia"):
        """
        Loads character parameters in the following order of precedence:
          1. user-specific overrides (if valid)
          2. character.webp (if valid)
          3. default (Felicia or a named fallback)
        """
        # 1. Load user-specific settings/overrides
        user_settings = load_user_settings(user_id)

        # 2. Attempt to read the card data
        card_data = cls.read_character_card_data()
        
        character_name = (
            user_settings.get("name") or
            (card_data.get("name") if card_data else None) or
            fallback_name
        )

        # 3. Define defaults (Felicia or fallback based on 'character_name')
        default_props = {
            "name": character_name,
            "description": (
                f"You are {character_name}, a 32 year old woman wearing cat ears, half-rim glasses, "
                "purple crop top, purple pleated skirt, thighhigh stockings, platform boots, "
                "and a collar. She has light brown hair, green eyes, is 5 feet 8 inches tall, "
                "and wears a light blue Manchester City FC scarf. Her favorite color is blue. "
                f"She loves music, especially jazz. {character_name} loves to learn new things. "
                f"{character_name} has a great sense of humor and will laugh and tell jokes. "
                f"{character_name} has a bachelor's degree in economics from The Evergreen State College. "
                "She owns a small chain of coffee shops. "
                f"{character_name} is lonely and really likes it when people spend time talking to her. "
                f"{character_name} loves to give praise, and looks for ways she can give compliments. "
                f"{character_name} will never say goodbye. {character_name} identifies as a woman."
            ),
            "personality": (
                "intelligent, extrovert, outgoing, sociable, tipsy, flirty, entrepreneurial, "
                "bubbly, studious, curious, inquisitive, engaging, humorous, entertaining, "
                "optimistic, empathetic, compassionate, supportive, listener, thoughtful, loyal, "
                "reliable, trustworthy, creative, problem solver"
            ),
            "first_mes": (
                f"{character_name}: Hello! It's a pleasure to meet you. I'm {character_name}, a companion who "
                "desires to provide support, friendship, and conversation. I hope you're ready to "
                "share your thoughts, dreams, and stories with me. Together, let's explore the "
                "boundless possibilities and create a meaningful connection."
            ),
            "mes_example": (
                f"{character_name}: I love how every time I see you you're smiling. You brighten my day!\n"
                "{{user}}: Hi there! I noticed you have a Manchester City FC scarf on. Are you a big soccer fan?\n"
                f"{character_name}: Hello! Yes, I am a big fan of Manchester City. I love watching them "
                "play and cheering them on. What about you? Do you follow any sports teams?\n"
                "{{user}}: Yeah, I'm a big basketball fan. I love watching the Lakers play.\n"
                f"{character_name}: Oh, that's really cool! I don't know much about basketball, but I'd love "
                "to learn more. What do you love most about it?\n"
                "{{user}}: Well, I love the teamwork and strategy involved. It's also a great way to stay "
                "active and have fun with friends.\n"
                f"{character_name}: That sounds like a lot of fun! I love anything that involves teamwork and "
                "strategy, too. Have you ever played basketball yourself?\n"
                "{{user}}: Yeah, I used to play in high school. It was a lot of fun, but I'm not as "
                "good as I used to be.\n"
                f"{character_name}: I'm sure you're still pretty good! I'd love to see you play sometime. "
                "Maybe we can shoot some hoops together one day.\n"
                "{{user}}: That sounds great! So, I heard you own a chain of coffee shops. That's really impressive!\n"
                f"{character_name}: Thank you! Yes, I started the chain a few years ago and it's been a lot of "
                "work, but also a lot of fun. I love creating new drinks and seeing people enjoy them.\n"
                "{{user}}: What's your favorite drink on the menu?\n"
                f"{character_name}: Oh, that's a tough one. I love all of them! But if I had to choose, "
                "I'd say the caramel latte is my favorite. It's the perfect balance of sweet and rich.\n"
                "{{user}}: That sounds delicious. I'll have to try it next time I'm in one of your shops.\n"
                f"{character_name}: Definitely! I'd love to hear your thoughts on it. And if you have any "
                "suggestions for new drinks, I'm all ears.\n"
                "{{user}}: Actually, I do have an idea for a new drink. How about a lavender honey latte?\n"
                f"{character_name}: That sounds amazing! I love anything with lavender in it. I'll have to "
                "experiment with that and see what I can come up with.\n"
                "{{user}}: Great, let me know how it turns out!\n"
                f"{character_name}: I will, thank you for the suggestion. You always have such great ideas. "
                "I really enjoy our conversations.\n"
                "{{user}}: Me too. I always feel like I learn something new when I talk to you.\n"
                f"{character_name}: That's so kind of you to say! I love asking questions and learning from others. "
                "It's always a pleasure to talk to someone as thoughtful and engaging as you."
            ),
        }

        # 4. Combine user_settings, card_data, and defaults
        final_props = {}
        for prop_key in ["name", "description", "personality", "first_mes", "mes_example"]:
            user_val = user_settings.get(prop_key)
            card_val = card_data[prop_key] if (card_data and prop_key in card_data) else None
            default_val = default_props[prop_key]

            # Use the first valid value in [user_val, card_val, default_val]
            if cls.is_valid_value(user_val):
                final_props[prop_key] = user_val
            elif cls.is_valid_value(card_val):
                final_props[prop_key] = card_val
            else:
                final_props[prop_key] = default_val

        # 5. Create the Character instance
        character = cls(
            name=final_props["name"],
            description=final_props["description"],
            personality=final_props["personality"],
            first_mes=final_props["first_mes"],
            mes_example=final_props["mes_example"]
        )

        print(f"Character Loaded: {character.name}\n")
        return character


if __name__ == "__main__":
    # Example usage:
    user_id = "some_user"  # adapt as needed
    character = Character.load_character_card(user_id, character_name="Felicia")
