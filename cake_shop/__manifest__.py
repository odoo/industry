{
<<<<<<< a9dd20c2a7dc035cf0d8113b30c6e5c9f3300e20
    'name': 'Cake Shop',
    'version': '1.2',
    'category': 'Retail',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'name': 'Cake Store',
    'version': '1.0',
    'category': 'Retail',
    'description': """
This setup is for bakery store companies selling to consumers. Bakery are businesses that carry a large selection of products: puffs , cakes , pastries etc...
""",
=======
    'name': 'Cake Store',
    'version': '1.0',
    'category': 'Food and Beverage',
    'description': """
This setup is for bakery store companies selling to consumers. Bakery are businesses that carry a large selection of products: puffs , cakes , pastries etc...
""",
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'calendar',
        'contacts',
        'knowledge',
        'pos_sale',
        'purchase_stock',
        'sale_purchase',
        'website_sale_collect',
        'website_sale_stock',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/pos_category.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
        'data/pos_config.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/res_company.xml',
        'demo/delivery_carrier.xml',
        'demo/ir_attachment.xml',
        'demo/res_partner.xml',
        'demo/product_supplierinfo.xml',
        'demo/product_product.xml',
        'demo/purchase_order.xml',
        'demo/sale_order.xml',
        'demo/website_view.xml',
        'demo/website_theme_apply.xml',
        'demo/payment_provider_demo_post.xml',
        'demo/website.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'cake_shop/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
        "demo/website_view.xml",
    ],
    'images': ['images/main.png'],
    'url': "https://www.odoo.com/trial?industry&selected_app=cake_shop",
    'website': "https://www.odoo.com/industries/cake-store",
}
