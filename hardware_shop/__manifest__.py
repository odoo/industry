{
    'name': 'Hardware Store',
<<<<<<< a9dd20c2a7dc035cf0d8113b30c6e5c9f3300e20
    'category': 'Retail',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'version': '1.0',
    'category': 'Retail',
    'description': """
For Hardware Stores that carry a large selection of products: plumbing, machinery, household, gardening, carpenter and electrical, etc.
Using Point of Sale, Inventory, Sales, Purchase, Accounting, Contact, Employee, Dashboard, Barcode, and Documents and E-commerce to grow their business.
    """,
=======
    'version': '1.0',
    'category': 'Retail and eCommerce',
    'description': """
For Hardware Stores that carry a large selection of products: plumbing, machinery, household, gardening, carpenter and electrical, etc.
Using Point of Sale, Inventory, Sales, Purchase, Accounting, Contact, Employee, Dashboard, Barcode, and Documents and E-commerce to grow their business.
    """,
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'barcodes',
        'base_geolocalize',
        'contacts',
        'knowledge',
        'pos_sale',
        'purchase_stock',
        'sale_loyalty',
        'sale_margin',
        'sale_purchase',
        'stock_delivery',
    ],
    'data': [
        'data/res_config_setting.xml',
        'data/ir_attachment_pre.xml',
        'data/product_category.xml',
        'data/pos_category.xml',
        'data/product_template.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_pricelist.xml',
        'data/product_pricelist_item.xml',
        'data/pos_payment_method.xml',
        'data/pos_config.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/product_quantity.xml',
        'demo/stock_warehouse_orderpoint.xml',
        'demo/res_partner.xml',
        'demo/product_supplierinfo.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/function_pickup.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'hardware_shop/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
    'url': "https://www.odoo.com/trial?industry&selected_app=hardware_shop",
    'website': "https://www.odoo.com/industries/hardware-store",
}
