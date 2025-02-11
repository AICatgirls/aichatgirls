from pytest_bdd import scenarios, given, when, then
import pytest
from settings import load_user_settings, save_user_settings
from unittest.mock import MagicMock

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
def when_user_sends_set_command(user, character):
    settings = load_user_settings(user, character)
    settings["max_response_length"] = 500
    save_user_settings(user, character, settings)

@then("The bot should update the setting and confirm the change")
def then_setting_should_be_updated(user, character):
    settings = load_user_settings(user, character)
    assert settings["max_response_length"] == 500
