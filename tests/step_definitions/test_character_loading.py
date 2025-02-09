from pytest_bdd import scenarios, given, when, then
import pytest
from loadCharacterCard import Character

scenarios("../features/character_loading.feature")

@pytest.fixture
def character():
    return None  # Placeholder for loading the character

@given("A character card exists")
def given_character_card_exists():
    pass  # Assume the character card is available

@pytest.fixture
@when("The bot loads the character card")
def when_bot_loads_character_card():
    character = Character.load_character_card("TestCharacter")
    return character


@then("The character's details should be available")
def then_character_details_are_available(when_bot_loads_character_card):
    assert when_bot_loads_character_card.name == "TestCharacter"
