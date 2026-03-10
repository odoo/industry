Feature: Work Items

    Background:
        Given a new SO
        And the unit with id = 1 as "units"
        And the work item form view from the SO

    Scenario: Create work item from SO without a template
        As a user, 
        I want to be able to create a work item from the sale order without creating a template,
        so that i don't pollute my work item templates library.

        When I open the form view
        And I set the following fields:
            | field            | alias_or_value  |
            | x_name           | random_string_0 |
            | x_unit_custom_id | units           |
        And I create a new work item line with a product in the form view
        And I save

        Then there exists exactly one SOL with product "random_string_0" in the SO
        And a work item is binded to the SOL with the product "random_string_0"
        And there exists exactly one work item with product "random_string_0"


    Scenario: Create work item template from SO
        As a user, 
        I want to be able to save a custom work item from the sale order wizard as work item template,
        so that i can easily grow my library when relevant straight from the sale order.

        When I open the form view
        And I set the following fields:
            | field            | alias_or_value  |
            | x_name           | random_string_1 |
            | x_unit_custom_id | units           |
        And I create a new work item line with a product in the form view
        And I save the work item form view
        And I open the work item form view of the SOL product "random_string_1"
        And I set the work item as a template

        Then there exists exactly one work item template with product "random_string_1"


    Scenario: Replace work item template from SO
        As a user, 
        I want to be able to replace a work item template from the sale order wizard,
        so that I make sure that only the most up to date template is leveraged afterward.

        Given the product of a new "random_string_2" work item template as "prod"

        When I open a SO form view
        And I create a new SOL for the field order_line in the form view with product_id = prod
        And I open the work item form view
        And I set the work item as a template

        Then there exists exactly one work item template with product "random_string_2"
