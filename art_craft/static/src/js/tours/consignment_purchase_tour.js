import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("consignment_purchase", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='purchase\\.menu_purchase_root']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] .o-autocomplete--input",
        "run": "edit demo"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_is_consignee'] input",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_field_product_label_section_and_note_cell .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_section_and_note_list_view tr:nth-child(3) > td",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_field_product_label_section_and_note_cell .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(5) > a",
        "run": "click"
    },
    {
        "trigger": ".o_section_and_note_list_view tr:nth-child(4) > td",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_confirm']",
        "run": "click"
    },
    {
        "trigger": ".o_stat_text",
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
