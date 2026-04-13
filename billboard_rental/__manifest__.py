{
    'name': 'Billboard Rental',
<<<<<<< 44142a93dfc6489c665550932c07f6317434cdf6
    'version': '1.2',
    'category': 'Services',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'version': '1.0',
    'category': 'Services',
    'description': """
This industry caters to billboard rental businesses, specializing in managing outdoor advertising spaces. It involves coordinating prime location leases, complying with regulations, and maximizing client visibility.
""",
=======
    'version': '1.0',
    'category': 'Business Services',
    'description': """
This industry caters to billboard rental businesses, specializing in managing outdoor advertising spaces. It involves coordinating prime location leases, complying with regulations, and maximizing client visibility.
""",
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'base_industry_data',
        'hr',
        'knowledge',
        'planning_field_service_sale_timesheet',
        'project_sale_subscription',
        'web_studio',
        'website_appointment',
        'website_crm',
        'worksheet',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_ui_menu.xml',
        'data/worksheet_template.xml',
        'data/account_analytic_account.xml',
        'data/project_task_type.xml',
        'data/project_project.xml',
        'data/sale_subscription_pricing.xml',
        'data/planning_role.xml',
        'data/product_product.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/crm_stage.xml',
        'data/website_view.xml',
        'data/website_theme_apply.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/appointment_type.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/res_partner.xml',
        'demo/account_analytic_plan.xml',
        'demo/account_analytic_account.xml',
        'demo/appointment_type.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
        'demo/hr_employee.xml',
        'demo/website_view.xml',
        'demo/website_theme_apply.xml',
        'demo/website.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'billboard_rental/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "data/website_view.xml",
        "static/src/js/my_tour.js",
        "demo/website_view.xml",
    ],
    'images': ['images/main.png'],
    'url': "https://www.odoo.com/trial?industry&selected_app=billboard_rental",
    'website': "https://www.odoo.com/industries/billboard-rental",
}
