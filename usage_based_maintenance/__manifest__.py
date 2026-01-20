{
    'name': 'Usage Based Maintenance',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'author': 'Odoo S.A.',
    'depends': [
        'industry_fsm_sale_report',
        'purchase',
        'quality_control',
        'sale_stock_renting',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_actions_server.xml',
        'data/ir_ui_view.xml',
        'data/ir_ui_menu.xml',
        'data/ir_model_access.xml',
        'data/ir_default.xml',
        'data/base_automation.xml',
    ],
    'license': 'OEEL-1',
    'cloc_exclude': [

    ],
    'images': ['images/main.png'],
    'website': "https://www.odoo.com/all-industries",
}
