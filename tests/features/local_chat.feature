Feature: Local Chat Functionality

  Scenario: User interacts with the bot in local mode
    Given The bot is running in local mode
    When A user sends a message
    Then The bot should respond appropriately
