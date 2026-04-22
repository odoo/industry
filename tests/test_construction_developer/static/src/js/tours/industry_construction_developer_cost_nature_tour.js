import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("industry_construction_developer_cost_nature_analysis_report_tour", {
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        "run": "click",
    },
    {
        "trigger": ".o_data_cell[name='name']:contains('S00003')",
        "run": "click",
    },
    {
        "trigger": ".oe_stat_button:contains('Cost Nature')",
        "run": "click",
    },
    {
        "trigger": ".o_group_has_content:contains('Equipment')",
        "run": "click",
    },
    {
        "trigger": ".o_group_has_content:contains('Equipment / Heavy Plant / Earth Moving')",
        "run": "click",
    },
    {
        "trigger": ".o_group_has_content:contains('Excavator')",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('Excavator')):has([name='x_work_item_id']:contains('Ground Preparation')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('Excavator')):has([name='x_work_item_id']:contains('Drainage System')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('Excavator')):has([name='x_work_item_id']:contains('Foundation Footing')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('Excavator')):has([name='x_work_item_id']:contains('Foundation Footing')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('Excavator')):has([name='x_work_item_id']:contains('Drainage System')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('Excavator')):has([name='x_work_item_id']:contains('Ground Preparation')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_facet_remove", // button in search bar to remove default sorting options 
        "run": "click",
    },
    {
        "trigger": ".o_searchview_input",
        "run": "click",
    },
    {
        "trigger": ".o_filter_menu .o-dropdown-item:contains('Labour')",
        "run": "click",
    },
    {
        "trigger": ".o_group_by_menu .o-dropdown-item:contains('Product')",
        "run": "click",
    },
    {
        "trigger": ".o_searchview_dropdown_toggler",
        "run": "click",
    },
    {
        "trigger": ".o_group_has_content:contains('General Labour')",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('General Labour')):has([name='x_work_item_id']:contains('Foundation Footing')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_data_row:has([name='x_product_id']:contains('General Labour')):has([name='x_work_item_id']:contains('Roofing')) .o_list_record_selector input",
        "run": "click",
    },
    {
        "trigger": ".o_unselect_all",
        "run": "click",
    },
    {
        "trigger": ".o_searchview_facet:contains('Labour') .o_facet_remove",
        "run": "click",
    },
    {
        "trigger": ".o_facet_remove",
        "run": "click",
    }
]
})
