{
    'name': 'Software Reseller',
    'version': '1.0',
<<<<<<< 875a02bf3c018b60fc4273a15eb87b232b13bfd4
    'category': 'Services',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'category': 'Services',
    'description': """
This setup if for IT companies reselling software licenses, and consulting services.🚀
The typical sale is a 1 year Oracle Database license that is purchased to Oracle, and resold to client at a margin, with extra services to setup the database.
""",
=======
    'category': 'Business Services',
    'description': """
This setup if for IT companies reselling software licenses, and consulting services.🚀
The typical sale is a 1 year Oracle Database license that is purchased to Oracle, and resold to client at a margin, with extra services to setup the database.
""",
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'knowledge',
        'project',
        'sale_planning',
        'sale_purchase',
        'sale_subscription',
        'sale_timesheet',
        'web_studio',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_ui_menu.xml',
        'data/project_task_type.xml',
        'data/product_category.xml',
        'data/account_analytic_plan.xml',
        'data/account_analytic_account.xml',
        'data/project_project.xml',
        'data/uom_uom.xml',
        'data/planning_role.xml',
        'data/product_product.xml',
        'data/sale_subscription_plan.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/product_supplierinfo.xml',
        'demo/product_product.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/project_task.xml',
        'demo/purchase_order_confirm.xml',
        'demo/planning_slot.xml',
        'demo/timesheet.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'software_reseller/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],
}
