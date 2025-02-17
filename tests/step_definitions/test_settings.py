from pytest_bdd import scenarios, given, when, then
import pytest
from unittest.mock import MagicMock, patch
from settings import load_user_settings, save_user_settings
from loadCharacterCard import Character

scenarios("../features/settings.feature")

@pytest.fixture
def user():
    return "TestUser"

@pytest.fixture
def character():
    return "TestBot"

@given("A user wants to change a bot setting")
def given_user_wants_to_change_setting():
    pass  # Precondition assumed

@when("The user sends the '/set max_response_length 500' command")
def when_user_sends_set_command(user):
    settings = load_user_settings(user)
    settings["max_response_length"] = 500
    save_user_settings(user, settings)

@then("The bot should update the setting and confirm the change")
def then_setting_should_be_updated(user):
    settings = load_user_settings(user)
    assert settings["max_response_length"] == 500

@pytest.fixture
@given("a user settings file containing character attributes")
def given_user_settings_with_character_attributes(user, character):
    from chatCommand import chat_command  # Import the command handler

    # Simulate user sending the command to update character attributes
    mock_message = MagicMock()
    mock_message.author = user
    mock_message.content = "/set character name CustomBot"
    chat_command(mock_message.content, mock_message, character)

    mock_message.content = "/set character description Custom Description"
    chat_command(mock_message.content, mock_message, character)

@pytest.fixture
@when("the character attributes are loaded")
def when_character_attributes_are_loaded(given_user_settings_with_character_attributes):
    settings = load_user_settings("TestUser")
    return settings.get("character_attributes")

@then("the character attributes in the settings file are applied")
def then_character_attributes_applied(when_character_attributes_are_loaded):
    assert when_character_attributes_are_loaded is not None, "Character attributes should be loaded but are missing."
    assert when_character_attributes_are_loaded == {"name": "CustomBot", "description": "Custom Description"}

@given("a user settings file that does not contain attributes")
def given_user_settings_without_character_attributes():
    with patch("settings.load_user_settings", return_value={}):
        yield

@then("the character card is loaded")
def then_character_card_is_loaded():
    with patch("loadCharacterCard.Character.load_character_card", return_value=Character("CardBot", "Card Description", "", "", "")) as mock_load:
        character = mock_load()
        assert character.name == "CardBot"
        assert character.description == "Card Description"

@given("no user settings file and no character card")
def given_no_user_settings_or_card():
    with patch("settings.load_user_settings", return_value={}), patch("loadCharacterCard.Character.load_character_card", side_effect=FileNotFoundError):
        yield

@then("the default character is used")
def then_default_character_is_used():
    default_character = Character("DefaultBot", "Default Description", "", "", "")
    assert default_character.name == "DefaultBot"
    assert default_character.description == "Default Description"
