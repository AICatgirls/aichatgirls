Feature: Character Loading

  Scenario: Load a character card
    Given A character card exists
    When The bot loads the character card
    Then The character's details should be available
