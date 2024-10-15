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
        "run": "edit gloster"
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
        "run": "edit on"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o_notebook_headers a[name='alternative_pos']",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o_create_button",
        "run": "click"
    },
    {
        "trigger": "main .o_field_widget[name='partner_id'] .o-autocomplete--input",
        "run": "edit ast"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_section_and_note_list_view a:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_field_product_label_section_and_note_cell .o-autocomplete--input",
        "run": "edit on"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='product_qty'] > .o_input",
        "run": "edit 100"
    },
    {
        "trigger": ".o-wysiwyg div[contenteditable='true']",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell[name='price_unit']",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='price_unit'] > .o_input",
        "run": "edit 110"
    },
    {
        "trigger": ".o-wysiwyg div[contenteditable='true']",
        "run": "click"
    },
    {
        "trigger": "footer > .o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o_cell button[name='action_compare_alternative_lines']",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(3) .o_clear_qty_buttons[name='action_choose']",
        "run": "click"
    },
    {
        "trigger": ".o_back_button > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_confirm']",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal button[name='action_cancel_alternatives']",
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
        "run": "edit lot001"
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
        "trigger": ".o_breadcrumb li:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_menu_brand",
        "run": "click"
    }
]
})
