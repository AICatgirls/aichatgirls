from pytest_bdd import scenarios, given, when, then
import pytest
from unittest.mock import MagicMock, patch
from chatHistory import ChatHistory
from chatCommand import chat_command
from loadCharacterCard import Character
from settings import load_user_settings, save_user_settings
from generate import generate_prompt_response

# Load scenarios from feature files
scenarios("../features/chat_commands.feature")

@pytest.fixture
def mock_message():
    mock = MagicMock()
    mock.author.display_name = "TestUser"
    mock.author.id = "456"
    mock.channel.id = 123
    mock.channel.name = "test-channel"
    mock.channel.guild = MagicMock()
    mock.channel.guild.name = "test-guild"
    mock.content = "This is a test message."
    return mock

@pytest.fixture
def test_character():
    return Character("TestBot", "Desc", "Personality", "Hello!", "Example")

@given("A user sends a message to the bot")
def given_user_message(mock_message):
    return mock_message

@pytest.fixture
@when("The user sends the '/help' command")
def when_user_sends_help_command(mock_message, test_character):
    mock_message.content = "/help"
    return chat_command(mock_message.content, mock_message, test_character)

@then("The bot should return a list of available commands")
def then_bot_returns_help_list(when_user_sends_help_command):
    assert "Available commands:" in when_user_sends_help_command
