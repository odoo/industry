import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('shop_booking_flow', {
    url: '/shop',
    steps: () => [
        {
            content: "Open product page",
            trigger: '.oe_product_image_link[title="Standard Room"]',
            expectUnloadPage: true,
            run: "click",
        },
        {
            content: "Check if the product is Standard Room",
            trigger: 'h1:contains("Standard Room")',
        },
        {
            content: "Check if product recurrence is displayed",
            trigger: '.o_renting_unit:contains("day")',
        },
        {
            content: "Check if rental date is displayed",
            trigger: '.o_website_sale_daterange_picker .attribute_name strong:contains("Rental Period")',
        },
        {
            content: "Check if warning message exists",
            trigger: 'span[name="renting_warning_message"]:contains("The product is not available for the following time period(s):")',
        },
        {
            content: "Check if the buy button is disabled",
            trigger: '#product_detail form #add_to_cart.disabled',
        },
        {
            content: "Select rental start date",
            trigger: '#rental_product_start_date',
            run: "click",
        },
        {
            content: "Check a selected cell is unavailable",
            trigger: '.o_date_item_cell.o_selected.o_daterangepicker_danger',
        },
        {
            content: "Select second last date as new start date",
            trigger: '.o_date_item_cell:not(.disabled.o_daterangepicker_danger)',
            run: () => {
                const cells = Array.from(document.querySelectorAll('.o_date_item_cell:not(.disabled.o_daterangepicker_danger)'));
                cells[cells.length - 2].click();
            },
        },
        {
            content: "Select last date as new end date",
            trigger: '.o_date_item_cell:not(.disabled.o_daterangepicker_danger)',
            run: () => {
                const cells = Array.from(document.querySelectorAll('.o_date_item_cell:not(.disabled.o_daterangepicker_danger)'));
                cells[cells.length - 1].click();
            },
        },
        {
            content: "Click outside the date picker to close it and save the selected dates",
            trigger: '#wrapwrap',
            run: "click",
        },
        {
            content: "Click the buy button",
            trigger: '#product_detail form #add_to_cart:not(.disabled)',
            expectUnloadPage: true,
            run: "click",
        },
        {
            content: "Click pay with demo button",
            trigger: 'button:contains("Pay with Demo")',
            run: "click",
        },
        {
            content: "Pay with demo",
            trigger: 'button[name="o_payment_submit_button"]',
            expectUnloadPage: true,
            run: "click",
        },
    ]
});
