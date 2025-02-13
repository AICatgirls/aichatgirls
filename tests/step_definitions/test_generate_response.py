from datetime import datetime
from pytest_bdd import scenarios, given, when, then
import pytest
from unittest.mock import MagicMock, patch
from generate import generate_prompt_response, call_openai, call_oobabooga
from loadCharacterCard import Character

scenarios("../features/generate_response.feature")

@pytest.fixture
def mock_message():
    mock = MagicMock()
    mock.author.display_name = "TestUser"
    mock.content = "Hello!"
    mock.created_at = datetime.now()
    mock.channel.name = "test-channel"
    mock.channel.id = 123
    return mock

@pytest.fixture
def test_character():
    return Character("TestBot", "Desc", "Personality", "Hello!", "Example")

@given("The bot is active")
def given_bot_is_active():
    pass  # Assume the bot is running

@given("The bot is active and OpenAI API is configured")
def given_bot_active_openai():
    patcher = patch("generate.OPENAI_API_KEY", "mocked-key")
    patcher.start()
    yield
    patcher.stop()

@given("The bot is active and OpenAI API is not configured")
def given_bot_active_no_openai():
    patcher = patch("generate.OPENAI_API_KEY", None)
    patcher.start()
    yield
    patcher.stop()

@pytest.fixture
@pytest.mark.asyncio
@when("A user sends a message")
async def when_user_sends_message(mock_message, test_character):
    with patch("generate.call_openai") as mock_openai, \
         patch("generate.call_oobabooga") as mock_oobabooga:

        mock_openai.return_value = "Test OpenAI response."
        mock_oobabooga.return_value = "Test Oobabooga response."

        return await generate_prompt_response(mock_message, test_character, "Test Context")

@pytest.fixture
@pytest.mark.asyncio
@when("A user sends a flagged message")
async def when_user_sends_flagged_message(mock_message, test_character):
    mock_message.content = "This is a flagged message."

    with patch("generate.moderate_input_with_requests") as mock_moderation:
        mock_moderation.return_value = {"results": [{"flagged": True}]}
        return await generate_prompt_response(mock_message, test_character, "Test Context")

@pytest.mark.asyncio
@then("The bot should generate an appropriate response")
async def then_bot_generates_response(when_user_sends_message):
    response = await when_user_sends_message
    assert response in ["Test OpenAI response.", "Test Oobabooga response."]

@pytest.mark.asyncio
@then("The bot should reject the message")
async def then_bot_rejects_message(when_user_sends_flagged_message):
    response = await when_user_sends_flagged_message
    assert response == "Sorry, but your input violates content guidelines."

@pytest.mark.asyncio
@then("The bot should call OpenAI's chat completion API")
async def then_calls_openai_api(mock_message, test_character):
    with patch("generate.call_openai") as mock_openai:
        mock_openai.return_value = "Test OpenAI response."
        response = await generate_prompt_response(mock_message, test_character, "Test Context")
        mock_openai.assert_called_once()
        assert response == "Test OpenAI response."

@pytest.mark.asyncio
@then("The bot should call the Oobabooga API")
async def then_calls_oobabooga_api(mock_message, test_character):
    with patch("generate.call_oobabooga") as mock_oobabooga:
        mock_oobabooga.return_value = "Test Oobabooga response."
        response = await generate_prompt_response(mock_message, test_character, "Test Context")
        mock_oobabooga.assert_called_once()
        assert response == "Test Oobabooga response."
