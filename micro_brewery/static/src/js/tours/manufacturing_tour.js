import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("manufacturing_tour", {
    url: "/odoo",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='mrp\\.menu_mrp_root']",
        "run": "click"
    },
    {
        "trigger": ".o_main_navbar",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='mrp\\.menu_mrp_manufacturing']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='mrp\\.menu_mrp_production_action']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "drag_and_drop .o_control_panel"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".oe_title > h1",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='product_id'] .o-autocomplete--input",
        "run": "edit blon"
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
        "trigger": ".o_menu_brand",
        "run": "click"
    },
    {
        "trigger": ".o_app[data-menu-xmlid='mrp_workorder\\.menu_mrp_workorder_root']",
        "run": "click"
    },
    {
        "trigger": ".o_control_panel_actions div:nth-child(1) > button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_mrp_display_record button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_control_panel_actions button:nth-child(2)",
        "run": "click"
    },
    {
        "trigger": ".o_mrp_display_record button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_control_panel_actions button:nth-child(3)",
        "run": "click"
    },
    {
        "trigger": ".o_mrp_display_record button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_control_panel_actions button:nth-child(4)",
        "run": "click"
    },
    {
        "trigger": ".o_mrp_display_record button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_mrp_display_record button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_home_menu",
        "run": "click"
    },
    {
        "trigger": ".o_app[data-menu-xmlid='mrp\\.menu_mrp_root']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='mrp\\.menu_mrp_manufacturing']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='mrp\\.menu_mrp_production_action']",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(4) > .o_data_cell[name='name']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_mark_done']",
        "run": "click"
    },
    {
        "trigger": ".o-default-button",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='lot_producing_id'] .o-autocomplete--input",
        "run": "edit 001"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='button_mark_done']",
        "run": "click"
    },
    {
        "trigger": ".o_menu_brand",
        "run": "click"
    }
]
})
