import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("bom_tour", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='mrp\\.menu_mrp_root']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='mrp\\.menu_mrp_bom']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='mrp\\.menu_mrp_bom_form_action']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='product_tmpl_id'] .o-autocomplete--input",
        "run": "edit sofa set (3+1"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell[name='product_id'] .o-autocomplete--input",
        "run": "edit sofa (triple "
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell[name='product_id'] .o-autocomplete--input",
        "run": "edit sofa (sing"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell[name='product_qty'] .o_input",
        "run": "edit 2"
    },
    {
        "trigger": ".o-mail-Thread > div",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o_menu_brand",
        "run": "click"
    },
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
        "run": "edit sofa set (3"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_confirm']",
        "run": "click"
    },
    {
        "trigger": ".o_button_icon",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_validate']",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal button[name='send_sms']",
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
