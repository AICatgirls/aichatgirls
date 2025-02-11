Feature: Chat History Management

  Scenario: User resets chat history
    Given A user has an existing chat history
    When The user sends the '/reset' command
    Then The chat history should be cleared
