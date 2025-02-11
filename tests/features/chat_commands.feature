Feature: Chat Commands

  Scenario: User requests help from the bot
    Given A user sends a message to the bot
    When The user sends the '/help' command
    Then The bot should return a list of available commands
