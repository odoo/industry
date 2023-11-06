# -*- coding: utf-8 -*-
{
    'name': 'Lawyer',
    'version': '1.0',
    'category': 'Services',
    'description': u"""
    This module insall a configuration that preset the modules and
    configuration of a law firm.
""",
    'author': 'Odoo S.A.',
    'depends': [
        'documents_project',
        'hr_timesheet',
        'knowledge',
        'project',
        'project_enterprise',
        'sale_management',
        'sale_planning',
        'sale_timesheet_enterprise',
        'website_appointment',
        'theme_clean',
    ],
    'data': [
        'data/ir_attachment_pre.xml',
        'data/documents_folder.xml',
        'data/project_project.xml',
        'data/product_template.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/appointment_type.xml',
    ],
    'demo': [
        'demo/ir_attachment_post.xml',
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/res_users.xml',
        'demo/appointment_type.xml',
        'demo/website.xml',
        'demo/website_page.xml',
    ],
    'application': False,
    'license': 'OPL-1',
    'images': ['images/main.png'],
}
