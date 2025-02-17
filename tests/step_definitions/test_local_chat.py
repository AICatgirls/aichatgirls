from pytest_bdd import scenarios, given, when, then
import pytest
from unittest.mock import MagicMock, patch
import asyncio

from generate import generate_prompt_response
from loadCharacterCard import Character

scenarios("../features/local_chat.feature")

@pytest.fixture
def mock_message():
    mock = MagicMock()
    mock.author.display_name = "LocalUser"
    mock.author.id = 12345  # So generate_prompt_response can look up user-specific data
    mock.content = "Hey bot!"
    mock.channel.name = "local_chat"
    return mock

@given("The bot is running in local mode")
def given_bot_in_local_mode():
    pass  # Assume local mode is active

@pytest.fixture
@when("A user sends a message")
@pytest.mark.asyncio
async def when_user_sends_message(mock_message):
    with patch("generate.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": [{"text": "Local response."}]}
        # Optionally mock loadCharacterCard to control character data:
        # with patch("loadCharacterCard.Character.load_character_card") as mock_load:
        #     mock_load.return_value = Character("TestBot", "Desc", "Personality", "Hello!", "Example")
        response = await generate_prompt_response(mock_message)
    return response

@then("The bot should respond appropriately")
@pytest.mark.asyncio
async def then_bot_responds_correctly(when_user_sends_message):
    response = when_user_sends_message
    assert response.startswith("Local response.")
