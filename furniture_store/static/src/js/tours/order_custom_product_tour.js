import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("order_custom_product_tour", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] .o-autocomplete--input",
        "run": "edit excellent furnit"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_field_product_label_section_and_note_cell .o-autocomplete--input",
        "run": "edit bed"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_sale_product_configurator_table li:nth-child(2) > div",
        "run": "click"
    },
    {
        "trigger": ".o_sale_product_configurator_table li:nth-child(2) input[name='ptal-1']",
        "run": "click"
    },
    {
        "trigger": ".o_sale_product_configurator_qty input[name='sale_quantity']",
        "run": "edit 16"
    },
    {
        "trigger": ".o_sale_product_configurator_table td:nth-child(2)",
        "run": "click"
    },
    {
        "trigger": ".o_sale_product_configurator_dialog button[name='sale_product_configurator_confirm_button']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_confirm']",
        "run": "click"
    },
    {
        "trigger": ".oe_stat_button[name='action_view_purchase_orders']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_confirm']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_view_picking']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_validate']",
        "run": "click"
    },
    {
        "trigger": ".o_breadcrumb li:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='delivery_count'] > .o_stat_text",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_validate']",
        "run": "click"
    },
    {
        "trigger": ".o_menu_brand",
        "run": "click"
    }
]
})
