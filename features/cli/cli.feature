Feature: CLI interface
  Scenario: Displaying the application version
    When I execute the version command
    Then the current application version is printed
    And the command exits successfully
