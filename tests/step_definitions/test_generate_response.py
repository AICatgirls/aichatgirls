from datetime import datetime
from pytest_bdd import scenarios, given, when, then
import pytest
from unittest.mock import MagicMock, patch
from generate import generate_prompt_response
from loadCharacterCard import Character

scenarios("../features/generate_response.feature")

@pytest.fixture
def mock_message():
    mock = type('', (), {})()  # Creates an empty object
    mock.author = type('', (), {"display_name": "TestUser", "__str__": lambda self: "TestUser"})()
    mock.content = "Hello!"
    mock.created_at = datetime.now()
    mock.channel = type('', (), {
        "guild": type('', (), {"name": "test-guild", "__str__": lambda self: "test-guild"})(),
        "name": "test-channel",
        "id": 123,
        "__str__": lambda self: "test-channel"
    })()
    return mock

@pytest.fixture
def test_character():
    return Character("TestBot", "Desc", "Personality", "Hello!", "Example")

@given("The bot is active")
def given_bot_is_active():
    pass  # Assume the bot is running

@pytest.fixture
@when("A user sends a message")
async def when_user_sends_message(mock_message, test_character):
    with patch("generate.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": [{"text": "Test response."}]}
        return await generate_prompt_response(mock_message, test_character, "Test Context")

@then("The bot should generate an appropriate response")
async def then_bot_generates_response(when_user_sends_message):
    response = await when_user_sends_message
    assert response.startswith("Test response.")
