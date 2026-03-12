{
    'name': 'Recurring Rental Billing',
    'category': 'Hidden/Tools',
    'author': 'Odoo S.A.',
    'depends': [
        'base_industry_data',
        'knowledge',
        'sale_management',
        'sale_renting',
        'web_studio',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_actions_server.xml',
        'data/ir_ui_view.xml',
        'data/sale_order_template.xml',
        'data/product_category.xml',
        'data/res_config_settings.xml',
    ],
    'license': 'OEEL-1',
    'images': ['images/main.png'],
    'website': "https://www.odoo.com/all-industries",
}
