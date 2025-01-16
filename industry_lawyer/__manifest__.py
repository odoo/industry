{
    'name': 'Law Firm',
    'version': '1.0',
    'category': 'Services',
    'description': """
This module installs a configuration that presets the modules and configure Odoo for a law firm.
""",
    'depends': [
        'contacts',
        'documents_project',
        'hr_timesheet',
        'knowledge',
        'project',
        'project_enterprise',
        'sale_management',
        'sale_timesheet_enterprise',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/project_task_type.xml',
        'data/project_project.xml',
        'data/project_task.xml',
        'data/product_product.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/hr_job.xml',
        'demo/hr_employee.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            'industry_lawyer/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
}
