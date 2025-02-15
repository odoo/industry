import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("sale_order_to_cash_tour", {
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
        "run": "edit alyssia santon"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item > a:contains('Alyssia Santon'), .fa-circle-o-notch",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_field_product_label_section_and_note_cell .o-autocomplete--input",
        "run": "edit ray-ban rb07"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": "li:nth-child(2) > .o_sale_product_configurator_ptav_color",
        "run": "click"
    },
    {
        "trigger": ".o_sale_product_configurator_price[name='price'] > button[name='sale_product_configurator_add_button']",
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
        "trigger": ".o_stat_info",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_validate']",
        "run": "click"
    },
    {
        "trigger": ".o_back_button > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='\\36 32']",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal button[name='create_invoices']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_post']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_register_payment']",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal button[name='action_create_payments']",
        "run": "click"
    },
    {
        "trigger": ".o_menu_toggle",
        "run": "click"
    }
]
})
