{
    'name': 'Construction-cost Architecture Fees',
    'category': 'Services',
    'author': 'Odoo S.A.',
    'license': 'OEEL-1',
    'depends': ['base_automation', 'sale_management', 'sale_project', 'web_studio'],
    'data': [
        'data/ir_module_module_dependency.xml',
        'data/ir_model_fields.xml',
        'data/product_product.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/ir_ui_view.xml',
    ],
    'cloc_exclude': ['data/ir_module_module_dependency.xml'],
}
