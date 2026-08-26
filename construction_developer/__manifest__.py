{
    'name': 'Construction Developer',
    'version': '2.1',
    'category': 'Construction',
    'depends': [
        'base_industry_data',
        'construction',
        'mrp',
        'web_gantt',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/stock_location.xml',

        'features/product/automate_cost_update.xml',

        'features/remarks/project_project.xml',
        'features/remarks/project_task.xml',
        'features/remarks/menus_and_task_override.xml',
        'data/project_tags.xml',

        'features/sale/sol_numbering.xml',
        'features/stock/so_worksite_loc/so_worksite_loc.xml',
        'features/stock/route_configs.xml',
        'features/stock/so_confirm_link_stock.xml',
        'features/mrp/so_confirm_link_mrp.xml',
        'features/bom_template/bom_template_and_routes.xml',
        'features/bom_cost/bom_cost.xml',
        'features/bom_template/sol_bom_access.xml',
        'features/bom_cost/so_bom_cost_updates.xml',
        'features/stock/so_worksite_loc/bridge_so_bom_cost_updates.xml',
        'features/stock/so_stock.xml',
        'features/purchase/po_confirm_link_picking.xml',
        'features/project/so_o2m.xml',
        'features/mrp/delivery_progress.xml',
        'features/sale/contract_type.xml',
        'features/mrp/work_breakdown_structure/override_deadline_with_custom_field.xml',
        'features/mrp/work_breakdown_structure/work_breakdown_structure.xml',


        'features/product/cost_nature.xml',
        'data/product_category.xml',

        'features/spreadsheet_dashboard/progress_approver.xml',
        'features/spreadsheet_dashboard/reports.xml',

        'data/views_standard.xml',
        'data/qweb_view.xml',


        'data/products.xml',
        'data/products_with_boms.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
    ],
    'demo': [
        'demo/stock_location.xml',
        'demo/res_company.xml',
        'demo/sale_order_post.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_developer/static/src/js/sol_numbering.js',
        ],
    },
    'cloc_exclude': [
        'data/qweb_view.xml',
    ],
    'images': ['images/main.png'],
    'license': 'OEEL-1',
    'application': True,
    'author': 'Odoo S.A.',
    'url': "https://www.odoo.com/trial?industry&selected_app=construction_developer",
    'website': "https://www.odoo.com/all-industries",
}
