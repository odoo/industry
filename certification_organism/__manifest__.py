{
    'name': 'Audit & Certification',
    'version': '1.0',
    'category': 'Services',
    'description': """
This module setup your database to easily use odoo in a Audit & Certification company.
""",
    'depends': [
        'web_studio',
        'knowledge',
        'industry_fsm_sale_report',
        'project',
        'hr_timesheet',
        'hr_holidays',
        'crm',
        'sale_timesheet',
        'product_margin',
        'website_appointment'
    ],
    'data': [
        'data/res_config_setting.xml',
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_model_access.xml',
        'data/ir_rule.xml',
        'data/project_task_type.xml',
        'data/account_analytic_plan.xml',
        'data/account_analytic_account.xml',
        'data/worksheet_template.xml',
        'data/project_project.xml',
        'data/product_product.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/ir_attachment_post.xml',
        'data/website_view.xml',
        'data/website_page.xml',
        'data/website_menu.xml',
        'data/ir_model_data.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/website.xml',
        'demo/res_partner.xml',
        'demo/hr_leave.xml',
        'demo/crm_tag.xml',
        'demo/crm_lead.xml',
        'demo/project_tags.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post_action.xml',
        'demo/x_control_charging_station.xml',
    ],
    'license': 'OPL-1',
    'assets': {
        'web.assets_backend': [
            'certification_organism/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'images': ['images/main.png'],

}
