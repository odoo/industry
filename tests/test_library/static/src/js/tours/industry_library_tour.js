import { registry } from '@web/core/registry';


registry.category('web_tour.tours').add('industry_library_tour', {
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid=\'library\\.return_main_menu\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-dropdown-item[data-menu-xmlid=\'library\\.return_settings_menu\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_data_row:contains("Return 7 days") > .o_list_record_selector input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_data_row:contains("Return 7 days") .o_field_widget[name=\'x_pos_product_category_ids\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--dropdown-item:contains("Games") > a',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o_data_row:contains("Return 7 days") .o_field_widget[name=\'x_pos_product_category_ids\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--dropdown-item:contains("Audio & Video") > a',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o_data_row:contains("Return 7 days") > .o_list_record_selector input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_data_row:contains("Return 14 days") > .o_list_record_selector input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_data_row:contains("Return 14 days") .o_field_widget[name=\'x_pos_product_category_ids\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--dropdown-item:contains("Games") > a',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o_data_row:contains("Return 14 days") .o_tag_badge_text',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_delete',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_data_row:contains("Return 14 days") .o_field_widget[name=\'x_pos_product_category_ids\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-autocomplete--dropdown-item:contains("Books") > a',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-dropdown-item[data-menu-xmlid=\'library\\.return_sub_menu\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            isActive: ['auto'],
            trigger: '.o_kanban_renderer:has(.o_widget_web_ribbon)',
        },
        {
            trigger: '.o_facet_remove',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_searchview_input',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-dropdown-item > span > span',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_searchview_dropdown_toggler',
            run: 'click',
            tooltipPosition: 'bottom',
        },
        {
            trigger: '.o_kanban_group:contains(\'WH/RET/00001\') footer',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_optional_columns_dropdown_toggle',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o-checkbox > input[name=\'date\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'date_deadline\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'picked\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'location_final_id\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'location_final_id\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'description_picking\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'date_deadline\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o-checkbox > input[name=\'picked\']',
            run: 'click',
            tooltipPosition: 'left'
        },
        {
            trigger: '.o_optional_columns_dropdown_toggle',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_data_row:contains("Friends") > .o_data_cell[name=\'date\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_date_item_cell.o_today',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_datetime_buttons > button:contains("Apply")',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_field_widget[name=\'quantity\'] > .o_input',
            run: 'edit 0',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_form_button_save',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_statusbar_buttons > button[name=\'button_validate\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_technical_modal button[name=\'process\']',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            trigger: '.o_back_button > a',
            run: 'click',
            tooltipPosition: 'bottom'
        },
        {
            isActive: ['auto'],
            trigger: '.o_kanban_renderer:not(:has(.o_widget_web_ribbon))',
        },
    ]
})
