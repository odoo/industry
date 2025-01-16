{
    'name': 'Land Surveyor',
    'version': '2.0',
    'category': 'Services',
    'description': """
This setup is for industrial companies who are into sureveying and measurement activities.
It may include surveying of building properties and the measurement of completed construction activities.
""",
    'depends': [
        'appointment_account_payment',
        'crm_enterprise',
        'documents_project',
        'knowledge',
        'sale_crm',
        'sale_management',
    ],
    'data': [
        'data/ir_attachment_pre.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        "data/knowledge_article_favorite.xml",
        "data/mail_message.xml",
        "data/knowledge_tour.xml",
    ],
    'demo': [
        'demo/account_analytic_plan.xml',
        'demo/account_analytic_account.xml',
        'demo/res_partner.xml',
        'demo/crm_lead.xml',
        "demo/mail_activity.xml",
        'demo/project_task_type.xml',
        'demo/project_project.xml',
        'demo/project_task.xml',
    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            'surveyor/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
}
