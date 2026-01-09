{
    'name': 'Mental Therapy',
    'version': '1.0',
    'category': 'Health and Fitness',
    'author': 'Odoo S.A.',
    'depends': [
        'wellness_practitioner',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/crm_stage.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/product_product.xml',
        'data/mail_message.xml',
        'data/knowledge_article_favorite.xml',
    ],
    'demo': [
        'demo/payment_provider_demo.xml',
        'demo/appointment_type.xml',
        'demo/res_partner.xml',
        'demo/crm_lead.xml',
        'demo/calendar_event.xml',
        'demo/res_users.xml',
        'demo/account_move.xml',
        'demo/account_move_line.xml',
        'demo/account_move_post.xml',
    ],
    'license': 'LGPL-3',
    'cloc_exclude': [
        'data/knowledge_article.xml',
    ],
    'images': [
        'images/main.png',
    ],
    'url': "https://www.odoo.com/trial?industry&selected_app=mental_therapy",
    'website': "https://www.odoo.com/all-industries",
}
