{
    'name': 'Construction Progress Management',
    'category': 'Hidden/Tools',
    'depends': [
        'base_industry_data',
        'construction',
        'construction_line_numbering',
        'web_studio',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_actions_server.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_embedded_actions.xml',
        'data/project_project.xml',
        'data/base_automation.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_progress_management/static/src/widgets/apply_to_section_widget.js',
            'construction_progress_management/static/src/widgets/apply_to_section_widget.xml',
        ],
    },
    'demo': [
        'demo/project_project.xml',
    ],
    'cloc_exclude': [
        "static/src/widgets/apply_to_section_widget.xml",
        "static/src/widgets/apply_to_section_widget.js",
    ],
    'license': 'OPL-1',
    'author': 'Odoo S.A.',
}
