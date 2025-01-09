import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("customer_order_tour", {
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
        "trigger": ".o-kanban-button-new",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='name'] .o_input",
        "run": "edit Media Burn: Ant Farm and making of image"
    },
    {
        "trigger": ".o_inner_group:nth-child(1) > .o_wrap_field:nth-child(1) > .o_cell:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='barcode'] > .o_input",
        "run": "edit 9781941753355"
    },
    {
        "trigger": ".o_notebook_headers a[name='purchase']",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--input",
        "run": "edit my book di"
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
        "run": "edit hanna"
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
        "run": "edit media burn: ant"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_confirm']",
        "run": "click"
    }
]
})
