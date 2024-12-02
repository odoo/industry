{
    'name': 'Cake Store',
    'version': '1.0',
    'category': 'Retail',
    'description': """
This setup is for bakery store companies selling to consumers. Bakery are businesses that carry a large selection of products: puffs , cakes , pastries etc...
""",
    'depends': [
        'knowledge',
        'pos_sale',
        'purchase_stock',
        'sale_mrp',
        'sale_purchase',
        'website_sale_stock',
        'theme_bistro',
    ],
    'data': [
        'data/ir_attachment_pre.xml',
        'data/product_category.xml',
        'data/product_template.xml',
        'data/product_product.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/mrp_bom.xml',
        'data/mrp_bom_line.xml',
        'data/res_config_settings.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/ir_attachment.xml',
        'demo/mrp_order_point.xml',
        'demo/mrp_order_point_order.xml',
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/product_supplierinfo.xml',
        'demo/product_product.xml',
        'demo/purchase_order.xml',
        'demo/sale_order.xml',
        'demo/website_view.xml',
        'demo/website_theme_apply.xml',
        'demo/payment_provider_demo_post.xml',
    ],
    'license': 'OPL-1',
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
}
