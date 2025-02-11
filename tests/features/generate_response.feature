Feature: AI Response Generation

  Scenario: User sends a message and receives a response
    Given The bot is active
    When A user sends a message
    Then The bot should generate an appropriate response
