import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("deposit_management_tour", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='sale\\.product_menu_catalog']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='sale\\.menu_product_template_action']",
        "run": "click"
    },
    {
        "trigger": ".o_kanban_record:nth-child(19) > main > span:nth-child(2)",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_deposit_product_1'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(4) > a",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='sale\\.sale_order_menu']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='sale\\.menu_sale_quotations']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] .o-autocomplete--input",
        "run": "edit gourmet"
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
        "run": "edit mobius tri"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_confirm']",
        "run": "click"
    },
    {
        "trigger": ".oe_stat_button[name='action_view_delivery']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_validate']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='\\34 10']",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--input",
        "run": "edit deposit"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(4) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='quantity'] > .o_input",
        "run": "edit 3"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--input",
        "run": "edit depo"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(3) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='quantity'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_technical_modal button[name='action_create_returns']",
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
        "trigger": ".o_statusbar_buttons > button[name='\\37 21']",
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
        "trigger": ".o_menu_brand",
        "run": "click"
    }
]
})
