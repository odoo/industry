{
    'name': 'Fossil Fuel Trading',
<<<<<<< a9dd20c2a7dc035cf0d8113b30c6e5c9f3300e20
    'category': 'Supply Chain',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'version': '1.0',
    'category': 'Supply Chain',
    'description': """
        The module specializes in trading coal and petroleum products, acquiring them from international
        suppliers or local vendors and reselling them to customers. They have a unique quality-checking
        method during the procurement process, defining specific parameters in the GRN and Delivery stages
        to ensure product quality.
    """,
=======
    'version': '1.0',
    'category': 'Business Services',
    'description': """
        The module specializes in trading coal and petroleum products, acquiring them from international
        suppliers or local vendors and reselling them to customers. They have a unique quality-checking
        method during the procurement process, defining specific parameters in the GRN and Delivery stages
        to ensure product quality.
    """,
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'account_asset',
        'base_automation',
        'calendar',
        'knowledge',
        'purchase_product_matrix',
        'quality_control_worksheet',
        'sale_product_matrix',
        'stock_delivery',
        'stock_dropshipping',
        'stock_landed_costs',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/base_automation.xml',
        'data/ir_actions_server.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/product_category.xml',
        'data/worksheet_template.xml',
        'data/product_template.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template_attribute_line.xml',
        'data/product_product.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/quality_point.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/res_partner.xml',
        'demo/product_supplierinfo.xml',
        'demo/stock_lot.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_post.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'coal_petroleum/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
    'url': "https://www.odoo.com/trial?industry&selected_app=coal_petroleum",
    'website': "https://www.odoo.com/industries/fossil-fuel-trading",
}
