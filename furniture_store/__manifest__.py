{
    'name': 'Furniture Store',
    'version': '1.0',
<<<<<<< 963a469a5cd46e1f01cc10a2bf188f2eeeee46a4
    'category': 'Retail',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'category': 'Retail',
    'description': """
This module sets up a furniture store for selling furniture like chairs, sofas, dining tables, ...
""",
=======
    'category': 'Retail and eCommerce',
    'description': """
This module sets up a furniture store for selling furniture like chairs, sofas, dining tables, ...
""",
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'knowledge',
        'mrp',
        'pos_sale',
        'sale_margin',
        'sale_purchase',
        'website_crm',
        'website_sale_stock',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/knowledge_attachments.xml',
        'data/product_public_category.xml',
        'data/product_category.xml',
        'data/stock_route.xml',
        'data/pos_category.xml',
        'data/product_template.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_pricelist.xml',
        'data/product_pricelist_item.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/mrp_bom.xml',
        'data/mrp_bom_line.xml',
        'data/pos_payment_method.xml',
        'data/pos_config.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/crm_lead.xml',
        'demo/product_supplierinfo.xml',
        'demo/product_template.xml',
        'demo/stock_quant.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_confirm.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/stock_picking_validation.xml',
        'demo/website_attachments.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/payment_provider_demo_post.xml',
        'demo/website.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'furniture_store/static/src/js/my_tour.js',
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
