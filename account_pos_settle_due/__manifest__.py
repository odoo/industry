{
    'name': 'Account - Point of Sale Settle Due',
    'category': 'Point of Sale',
    'author': 'Odoo S.A.',
    'depends': [
        'pos_settle_due',
        'web_studio',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_ui_view.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'license': 'OEEL-1',
}
