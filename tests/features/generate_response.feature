Feature: AI Response Generation

  Scenario: User sends a message and receives a response
    Given The bot is active
    When A user sends a message
    Then The bot should generate an appropriate response

  Scenario: User sends a message that violates moderation rules
    Given The bot is active
    When A user sends a flagged message
    Then The bot should reject the message

  Scenario: AI uses OpenAI API to generate a response
    Given The bot is active and OpenAI API is configured
    When A user sends a message
    Then The bot should call OpenAI's chat completion API

  Scenario: AI uses Oobabooga API to generate a response
    Given The bot is active and OpenAI API is not configured
    When A user sends a message
    Then The bot should call the Oobabooga API
