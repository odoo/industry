import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("purchase_custom_tour", {
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
        "run": "edit biocon"
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
        "run": "edit acetratine"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='product_qty'] > .o_input",
        "run": "edit 12"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] .o-autocomplete--input",
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
        "trigger": ".o_data_cell:nth-child(5) > button[name='Open\\ Move']",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell[name='lot_name']",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='lot_name'] > .o_input",
        "run": "edit lot-111"
    },
    {
        "trigger": "footer > .o_form_button_save",
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
        "trigger": ".o_menu_brand",
        "run": "click"
    }
]
})
