{
    'name': 'Non Profit Organization',
    'version': '1.0',
    'category': 'NGO',
    'description': """
    Non Profit Organization

    This industry module pre-configure odoo for non profit organizations.
""",
    'depends': [
        'knowledge',
        'mass_mailing',
        'sale_subscription',
        'web_studio',
        'website_crm',
        'website_event_sale',
        'theme_treehouse',
    ],
    'data': [
        'data/filters.xml',
        'data/account_analytic_plan.xml',
        'data/mail_template.xml',
        'data/product_product.xml',
        'data/product_pricelist.xml',
        'data/product_pricelist_item.xml',
        'data/sale_subscription_plan.xml',
        'data/sale_subscription_pricing.xml',
        'data/ir_actions_server.xml',
        'data/base_automation.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/knowledge_article_attachments.xml',
        'data/mail_message.xml',
        'data/res_config_settings.xml',
    ],
    'demo': [
        'demo/event_event.xml',
        'demo/event_event_ticket.xml',
        'demo/website.xml',
        'demo/website_page_views.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/website_attachment.xml',
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
}
