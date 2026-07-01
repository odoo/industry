{
    'name': 'Construction Developer',
    'version': '2.0',
    'category': 'Construction',
    'depends': [
        'base_industry_data',
        'construction',
        'mrp',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/stock_location.xml',
        'features/work_items/create_worksite_location_on_so_confirm.xml',
        'features/work_items/route_configs.xml',
        'features/work_items/link_loc_bom_on_so_confirm.xml',
        'features/work_items/product_bom_template_and_routes.xml',
        'features/work_items/bom_margin.xml',
        'features/work_items/update_sol_price_from_bom.xml',
        'features/work_items/access_bom_from_so.xml',
        'features/work_items/check_so_bom_price_updates.xml',
        'data/views_standard.xml',
    ],
    'demo': [
        'demo/dummy.xml',
    ],
    'cloc_exclude': [
    ],
    'images': ['images/main.png'],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
    'url': "https://www.odoo.com/trial?industry&selected_app=construction_developer",
    'website': "https://www.odoo.com/all-industries",
}
