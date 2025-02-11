from chatHistory import ChatHistory
from datetime import datetime
from loadCharacterCard import Character
import pytest
from pytest_bdd import scenarios, given, when, then
from unittest.mock import MagicMock

scenarios("../features/chat_history.feature")

@pytest.fixture
def mock_message():
    mock = type('', (), {})()  # Creates an empty object
    mock.author = type('', (), {"display_name": "TestUser", "__str__": lambda self: "TestUser"})()
    mock.content = "Test message"
    mock.created_at = datetime.now()
    mock.channel = type('', (), {
        "guild": type('', (), {"name": "test-guild", "__str__": lambda self: "test-guild"})(),
        "name": "test-channel",
        "id": 123,
        "__str__": lambda self: "test-channel"
    })()
    return mock

@pytest.fixture
def chat_history(mock_message):
    return ChatHistory(mock_message, "TestBot")

@given("A user has an existing chat history")
def given_existing_chat_history(chat_history):
    chat_history.save({"messages": [{"user": "TestUser", "message": "Hello!"}]})

@when("The user sends the '/reset' command")
def when_user_resets_chat_history(chat_history):
    chat_history.reset()

@then("The chat history should be cleared")
def then_chat_history_should_be_cleared(chat_history):
    assert len(chat_history.load(Character("TestBot", "", "", "", ""), "TestUser")["messages"]) == 0
