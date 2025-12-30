{
    'name': 'Construction Remarks',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'depends': [
        'base_industry_data',
        'construction',
        'project',
        'web_studio',
    ],
    'data': [
        'data/ir_model.xml',
        'data/ir_model_access.xml',
        'data/ir_model_fields.xml',
        'data/project_task_type.xml',
        'data/ir_default.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_ui_menu.xml',
        'data/ir_embedded_actions.xml',
        'data/project_project.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_remarks/static/src/js/kanban_controller.js',
            'construction_remarks/static/src/js/relational_model.js',
        ],
    },
    'cloc_exclude': [
        "static/src/js/kanban_controller.js",
        "static/src/js/relational_model.js",
    ],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
}
