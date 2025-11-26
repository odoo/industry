{
    'name': 'Deposit Management',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'depends': [
        'base_automation',
        'mrp_workorder',
        'purchase_stock',
        'sale',
        'web_studio',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/qweb_view.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_default.xml',
        'data/product_category.xml',
        'data/account_tax.xml',
        'data/res_config_settings.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'cloc_exclude': [
        'data/qweb_view.xml',
    ],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
    'images': ['images/main.png'],
}
