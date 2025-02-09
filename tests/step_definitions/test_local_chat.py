from pytest_bdd import scenarios, given, when, then
import pytest
from unittest.mock import MagicMock, patch
from generate import generate_prompt_response
from loadCharacterCard import Character

scenarios("../features/local_chat.feature")

@pytest.fixture
def mock_message():
    mock = MagicMock()
    mock.author.display_name = "LocalUser"
    mock.content = "Hey bot!"
    mock.channel.name = "local_chat"
    return mock

@pytest.fixture
def test_character():
    return Character("TestBot", "Desc", "Personality", "Hello!", "Example")

@given("The bot is running in local mode")
def given_bot_in_local_mode():
    pass  # Assume local mode is active

@pytest.fixture
@when("A user sends a message")
def when_user_sends_message(mock_message, test_character):
    with patch("generate.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": [{"text": "Local response."}]}
        return generate_prompt_response(mock_message, test_character, "Local Context")

@then("The bot should respond appropriately")
async def then_bot_responds_correctly(when_user_sends_message):
    response = await when_user_sends_message  # Await the coroutine
    assert response.startswith("Local response.")
