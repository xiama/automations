@internals
Feature: PHP Application

  # runcon -u ?? -r system_r -t libra_initrc_t

  Scenario: Add Remove Alias a PHP Application
    Given an accepted node
    And a new guest account
    And a new php application
    And the php application is running
    When I add-alias the php application
    Then the php application will be aliased
    When I remove-alias the php application
    Then the php application will not be aliased 
    
