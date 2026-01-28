{
    'name': 'Physical Therapy',
    'version': '1.0',
    'category': 'Health and Fitness',
    'author': 'Odoo S.A.',
    'depends': [
        'appointment_account_payment',
        'appointment_crm',
        'knowledge',
        'sale_crm',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
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
        'data/product_product.xml',
    ],
    'demo': [
        'demo/payment_provider_demo.xml',
        'demo/res_partner.xml',
        'demo/crm_lead.xml',
        'demo/calendar_event.xml',
        'demo/res_users.xml',
        'demo/account_move.xml',
        'demo/account_move_line.xml',
        'demo/account_move_post.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'physical_therapy/static/src/js/my_tour.js',
        ]
    },
    'license': 'OEEL-1',
    'cloc_exclude': [
        'data/knowledge_article.xml',
        "static/src/js/my_tour.js",
    ],
    'images': [
        'images/main.png',
    ],
    'url': "https://www.odoo.com/trial?industry&selected_app=physical_therapy",
    'website': "https://www.odoo.com/all-industries",
}
