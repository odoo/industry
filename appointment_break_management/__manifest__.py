{
    'name': 'Appointment Break Management',
    'category': 'Services',
    'depends': [
        'appointment',
        'base_automation',
        'calendar',
        'web_studio',
    ],
    'data': [
        'data/ir_module_module_dependency.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_actions_actions.xml',
        'data/uninstall_hook.xml',
    ],
    "cloc_exclude": [
        'data/ir_module_module_dependency.xml',
        'data/uninstall_hook.xml',
    ],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
    'images': ['images/main.png'],
}
