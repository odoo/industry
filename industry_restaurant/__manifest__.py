{
    'name': 'Fine Dining Restaurant',
    'version': '1.0',
<<<<<<< 98b59479dbd6d4bdf66cd9f7ecaf90bf01df2adc
    'category': 'Hospitality',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'category': 'Hospitality',
    'description': """
        This Odoo module is designed to streamline and enhance the management of your restaurant operations.
        Whether you own a fine dining establishment, a cafe, or fast-food joints, cafés, food trucks, cloud kitchens, and more.
    """,
=======
    'category': 'Food and Beverage',
    'description': """
        This Odoo module is designed to streamline and enhance the management of your restaurant operations.
        Whether you own a fine dining establishment, a cafe, or fast-food joints, cafés, food trucks, cloud kitchens, and more.
    """,
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'account_followup',
        'contacts',
        'hr',
        'knowledge',
        'planning',
        'pos_enterprise',
        'pos_loyalty',
        'pos_online_payment_self_order',
        'pos_restaurant_appointment',
        'project',
        'purchase_stock',
        'website_appointment',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/appointment_type.xml',
        'data/ir_attachment_pre.xml',
        'data/product_category.xml',
        'data/product_product.xml',
        'data/project_task_type.xml',
        'data/project_project.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/website_view.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/pos_payment_method.xml',
        'demo/payment_provider_demo_post.xml',
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/pos_config.xml',
        'demo/product_supplierinfo.xml',
        'demo/product_product.xml',
        'demo/kitchen_display.xml',
        'demo/product_packaging.xml',
        'demo/stock_warehouse_orderpoint.xml',
        'demo/planning_role.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_post.xml',
        'demo/planning_slot.xml',
        'demo/project_task.xml',
        'demo/appointment_type.xml',
        'demo/website_attachment.xml',
        'demo/website_view.xml',
        'demo/website_page.xml',
        'demo/website_menu.xml',
        'demo/website_theme_apply.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'industry_restaurant/static/src/js/my_tour.js',
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
