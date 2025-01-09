import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("purchase_lot_tour", {
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
        "run": "edit lg ai"
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
        "run": "edit lg dual "
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='product_qty'] > .o_input",
        "run": "edit 6"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_confirm']",
        "run": "click"
    },
    {
        "trigger": ".oe_stat_button[name='action_view_picking']",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell:nth-child(6) > button[name='Open\\ Move']",
        "run": "click"
    },
    {
        "trigger": ".o_widget:nth-child(1) > button",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='next_serial'] > .o_input",
        "run": "edit 21"
    },
    {
        "trigger": ".o-overlay-item:nth-child(2) button:nth-child(1)",
        "run": "click"
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
        "trigger": ".o_menu_brand",
        "run": "click"
    },
    {
        "trigger": ".o_app[data-menu-xmlid='stock\\.menu_stock_root']",
        "run": "click"
    },
    {
        "trigger": ".o_kanban_record:nth-child(1) .oe_kanban_action[name='get_action_picking_tree_ready']",
        "run": "click"
    },
    {
        "trigger": ".o_searchview_facet:nth-child(2) .o_facet_remove",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(13) > .o_data_cell[name='partner_id']",
        "run": "click"
    },
    {
        "trigger": ".o_menu_brand",
        "run": "click"
    }
]
})
