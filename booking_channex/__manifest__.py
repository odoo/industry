{
    'name': 'Booking Channex',
    'author': 'Odoo S.A.',
    'category': 'Hidden/Tools',
    'auto_install': True,
    'depends': [
        'planning',
        'sale_management',
        'web_studio',
    ],
    'data': [
        'data/ir_model.xml',
        'data/ir_model_access.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_model_fields.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_cron.xml',
        'data/ir_ui_view.xml',
        'data/ir_ui_menu.xml',
    ],
    'demo': [
        'demo/res_company.xml',
    ],
    'license': 'OEEL-1',
    'cloc_exclude': [
    ],
}
