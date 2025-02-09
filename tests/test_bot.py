import pytest
import pytest_asyncio
import json
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from chatHistory import ChatHistory
from chatCommand import chat_command
from loadCharacterCard import Character
from settings import load_user_settings, save_user_settings
from generate import generate_prompt_response

@pytest.fixture
def mock_message():
    mock = MagicMock()
    mock.author.display_name = "TestUser"
    mock.author.id = "456"  # Convert to a valid string ID
    mock.author.__str__.return_value = "TestUser"
    mock.channel.id = 123
    mock.channel.name = "test-channel"
    mock.channel.guild = MagicMock()
    mock.channel.guild.name = "test-guild"
    
    # Convert MagicMock values to strings for filename generation
    mock.channel.__str__.return_value = "test-channel"
    mock.channel.guild.__str__.return_value = "test-guild"
    
    # Ensure `content` is a string to prevent serialization issues
    mock.content = "This is a test message."
    
    # Fix the datetime issue by returning a timezone-aware UTC datetime
    mock.created_at = datetime.now(timezone.utc)

    return mock

@pytest.fixture
def chat_history(mock_message):
    return ChatHistory(mock_message, "TestBot")

# --- ChatHistory Tests ---
def test_chat_history_save_load(chat_history):
    character = Character("TestBot", "Desc", "Personality", "Hello!", "Example")
    test_data = {"messages": [{"user": "TestUser", "message": "Hello!"}]}
    chat_history.save(test_data)
    loaded_data = chat_history.load(character, "TestUser")
    assert loaded_data["messages"][0]["message"] == "Hello!"

def test_chat_history_reset(chat_history):
    character = Character("TestBot", "Desc", "Personality", "Hello!", "Example")
    chat_history.save({"messages": [{"user": "TestUser", "message": "Hello!"}]})
    chat_history.reset()
    
    # Ensure it matches the expected default messages
    loaded_data = chat_history.load(character, "TestUser")
    assert len(loaded_data["messages"]) == 2  # Expecting two default messages
    assert loaded_data["messages"][0]["message"] == "Example"

# --- ChatCommand Tests ---
def test_chat_command_help(mock_message):
    response = chat_command("/help", mock_message, Character("TestBot", "Desc", "Personality", "Hello!", "Example"))
    assert "Available commands:" in response

def test_chat_command_set(mock_message):
    with patch("chatCommand.whitelist.is_channel_whitelisted", return_value=True):
        mock_message.content = "/set max_response_length 500"  # Ensure correct format
        response = chat_command(mock_message.content, mock_message, Character("TestBot", "Desc", "Personality", "Hello!", "Example"))
        assert response is not None  # Ensure response isn't None
        assert "updated" in response.lower()

# --- Character Loading Tests ---
def test_character_loading():
    character = Character.load_character_card("TestCharacter")
    assert character.name == "TestCharacter"
    assert "TestCharacter" in character.first_mes

# --- Settings Tests ---
def test_load_user_settings():
    settings = load_user_settings("TestUser", "TestBot")
    assert "max_response_length" in settings

def test_save_user_settings():
    settings = {"max_response_length": 500}
    save_user_settings("TestUser", "TestBot", settings)
    loaded_settings = load_user_settings("TestUser", "TestBot")
    assert loaded_settings["max_response_length"] == 500

# --- Generate Prompt Tests ---
@pytest.mark.asyncio
async def test_generate_prompt_response(mock_message):
    character = Character("TestBot", "Desc", "Personality", "Hello!", "Example")
    context = "This is a test context."
    
    with patch("generate.requests.post") as mock_post, \
         patch("generate.generate_prompt_response", return_value="Test response."):

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": [{"text": "Test response."}]}

        response = await generate_prompt_response(mock_message, character, context)
        assert response.startswith("Hello")
