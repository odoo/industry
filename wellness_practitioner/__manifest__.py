{
    'name': 'Wellness Practitioner',
    'version': '1.0',
    'category': 'Health and Fitness',
    'description': """
This module is designed for wellness practitioners, offering a complete solution to manage appointments and client relationships. It supports practitioners in providing personalized care, handling billing efficiently, and streamlining operations with integrated CRM, treatment plans, and essential tools like invoicing and appointment management. Perfect for professionals focused on holistic health and well-being services.
""",
    'depends': [
        'appointment_account_payment',
        'appointment_crm',
        'knowledge',
        'sale_crm',
        'web_studio',
    ],
    'data': [
        'data/ir_attachment_pre.xml',
        'data/email_template.xml',
        'data/appointment_type.xml',
        'data/crm_stage.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/base_automation.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/crm_lead.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'wellness_practitioner/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    'images': ['images/main.png'],
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'license': 'OPL-1',
}
