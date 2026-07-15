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
        'features/work_items/create_worksite_loc_on_so_confirm.xml',
        'features/work_items/route_configs.xml',
        'features/work_items/link_mrp_loc_bom_on_so_confirm.xml',
        'data/views_standard.xml',
    ],
    'demo': [
        'demo/dummy.xml',
    ],
    'cloc_exclude': [
    ],
    'images': ['images/main.png'],
    'license': 'OEEL-1',
    'application': True,
    'author': 'Odoo S.A.',
    'url': "https://www.odoo.com/trial?industry&selected_app=construction_developer",
    'website': "https://www.odoo.com/all-industries",
}
