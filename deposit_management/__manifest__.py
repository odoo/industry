{
    'name': 'Deposit Management',
<<<<<<< 6d88a414f00bac1b48b11e4a9729ecb41a0d0e33
    'version': '1.1',
    'category': 'Supply Chain',
||||||| c4fc6ae65b24d5b2a8f06f2321cf5526e557636d
    'version': '1.1',
    'category': 'Inventory/Inventory',
=======
    'version': '1.2',
    'category': 'Inventory/Inventory',
>>>>>>> ca9aa949c3e8b6efadf250a0a592a41fe22f035c
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
    'cloc_exclude': [
        'data/qweb_view.xml',
    ],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
    'images': ['images/main.png'],
}
