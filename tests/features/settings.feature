Feature: User Settings Management

  Scenario: User updates a bot setting
    Given A user wants to change a bot setting
    When The user sends the '/set max_response_length 500' command
    Then The bot should update the setting and confirm the change
