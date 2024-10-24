import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("sale_flow_tour", {
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
        "run": "edit glaencore"
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
        "run": "edit anth"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_sale_product_configurator_qty input[name='sale_quantity']",
        "run": "edit 100"
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
        "trigger": ".o_menu_brand",
        "run": "click"
    },
    {
        "trigger": ".o_app[data-menu-xmlid='stock\\.menu_stock_root']",
        "run": "click"
    },
    {
        "trigger": ".o_kanban_record:nth-child(4) .oe_kanban_action[name='get_action_picking_tree_ready']",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(4) > .o_data_cell[name='name']",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_vehicle_no'] > .o_input",
        "run": "edit 1280aro"
    },
    {
        "trigger": ".o_data_cell:nth-child(9) > button[name='Open\\ Move']",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='move_line_ids'] .o_data_cell[name='quantity']",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='move_line_ids'] .o_field_widget[name='quantity'] > .o_input",
        "run": "edit 100"
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
        "trigger": ".o_kanban_record:nth-child(5) .oe_kanban_action[name='get_action_picking_tree_ready']",
        "run": "click"
    },
    {
        "trigger": ".o_data_cell[name='location_dest_id']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='check_quality']",
        "run": "click"
    },
    {
        "trigger": ".o_act_window .o_form_sheet",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_test_type_1'] > .o_input",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_net_calorific_value'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_field_widget[name='x_ash_content'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_field_widget[name='x_moisture_content'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_field_widget[name='x_test_type'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_act_window .o_inner_group:nth-child(2)",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='x_total_sulphur'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_field_widget[name='x_flying_substance'] > .o_input",
        "run": "edit 20"
    },
    {
        "trigger": ".o_field_widget[name='x_hardgrave_grindability_index'] > .o_input",
        "run": "edit 20"
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
        "trigger": ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(1) > .o_data_cell[name='partner_id']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='\\35 27']",
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
