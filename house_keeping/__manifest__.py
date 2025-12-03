{
    'name': 'House Keeping',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'author': 'Odoo S.A.',
    'depends': [
        'booking_engine',
        'web_studio',
    ],
    'data': [
        'data/project_task_type.xml',
        'data/ir_model_fields.xml',
        'data/ir_default.xml',
        'data/project_project.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_cron.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_ui_view.xml',
        'data/ir_ui_menu.xml',
        'data/res_config_settings.xml',
    ],
    'demo': [
        'demo/planning_slot_post.xml',
    ],
    'license': 'OPL-1',
    'cloc_exclude': [
    ],
    'website': "https://www.odoo.com/all-industries",
}
