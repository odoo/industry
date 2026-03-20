Feature: Behave config

    Scenario: Validate module test behave structure
    Given an industry module with a behave test folder
    Then there should be at least one ".feature" file in "features" subdirectory
    And it should have a "features/steps" subdirectory
    And the file "steps.py" should exist in "features/steps" subdirectory
