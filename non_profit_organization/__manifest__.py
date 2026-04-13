{
    'name': 'Nonprofit Organization',
    'version': '1.0',
<<<<<<< 875a02bf3c018b60fc4273a15eb87b232b13bfd4
    'category': 'Services',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'category': 'Services',
    'description': """
    Non Profit Organization

    This industry module pre-configure odoo for non profit organizations.
""",
=======
    'category': 'Events, Community and Nonprofits',
    'description': """
    Non Profit Organization

    This industry module pre-configure odoo for non profit organizations.
""",
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'knowledge',
        'mass_mailing',
        'sale_subscription',
        'web_studio',
        'website_crm',
        'website_event_sale',
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
        'data/website_view.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/event_event.xml',
        'demo/event_event_ticket.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/website_attachment.xml',
        'demo/payment_provider_demo_post.xml',
        'demo/website.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'non_profit_organization/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "data/website_view.xml",
        "demo/website_view.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
}
