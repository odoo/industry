{
    'name': 'Agricultural Store',
<<<<<<< 870542a7109864cd9d3beb0bfafb9a9937f1ec2a
    'version': '1.2',
    'category': 'Retail',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'version': '1.0',
    'category': 'Retail',
    'description': """
    Tailored Setup for Agricultural Retail Businesses:
    This module is for B2B and B2C sales of farming products, including seeds, pesticides, plant nutrition, and equipment. The setup integrates all necessary modules (Point of Sale, Inventory, Sales, Purchase, ...) to run your business with the possibility to expand into online sales with the ecommerce and website applications.
""",
=======
    'version': '1.0',
    'category': 'Retail and eCommerce',
    'description': """
    Tailored Setup for Agricultural Retail Businesses:
    This module is for B2B and B2C sales of farming products, including seeds, pesticides, plant nutrition, and equipment. The setup integrates all necessary modules (Point of Sale, Inventory, Sales, Purchase, ...) to run your business with the possibility to expand into online sales with the ecommerce and website applications.
""",
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'crm',
        'knowledge',
        'pos_sale',
        'product_expiry',
        'purchase_requisition',
        'sale_purchase_stock',
        'web_studio',
        'website_sale_loyalty',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/pos_category.xml',
        'data/pos_config.xml',
        'data/product_category.xml',
        'data/product_pricelist.xml',
        'data/product_public_category.xml',
        'data/product_product.xml',
        'data/product_pricelist_item.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template_attribute_line.xml',
        'data/product_image.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/website_view.xml',
        'data/website_theme_apply.xml',
        'data/knowledge_tour.xml',
        'data/ir_ui_menu.xml',
        'data/product_ribbon.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/res_partner.xml',
        'demo/product_product.xml',
        'demo/crm_tag.xml',
        'demo/crm_lead.xml',
        'demo/mail_activity.xml',
        'demo/product_supplierinfo.xml',
        'demo/loyalty_program.xml',
        'demo/loyalty_rule.xml',
        'demo/loyalty_reward.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_post.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/loyalty_card.xml',
        'demo/sale_order_post.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
        'demo/website_ir_attachment.xml',
        'demo/payment_provider_demo_post.xml',
        'demo/website.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'agriculture_shop/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
        "data/website_view.xml",
        "demo/website_view.xml",
    ],
    'images': ['images/main.png'],
    'url': "https://www.odoo.com/trial?industry&selected_app=agriculture_shop",
    'website': "https://www.odoo.com/industries/agriculture-store",
}
