{
    'name': 'Odoo Partner',
    'version': '1.0',
    'category': 'Services',
    'depends': [
        'appointment_account_payment',
        'documents_project',
        'documents_spreadsheet',
        'knowledge',
        'sale_crm',
        'sale_pdf_quote_builder',
        'sale_timesheet',
        'sign',
    ],
    'data': [
        'data/ir_attachment_pre.xml',
        'data/documents_folder.xml',
        'data/product_pricelist.xml',
        'data/project_task_type.xml',
        'data/project_tags.xml',
        'data/project_project.xml',
        'data/project_task.xml',
        'data/product_product.xml',
        'data/product_pricelist_item.xml',
        'data/documents_document.xml',
        'data/quotation_document.xml',
        'data/sale_order_spreadsheet.xml',
        'data/sale_order_template.xml',
        'data/sale_order_template_line.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/appointment_type.xml',
        'data/res_config_settings.xml',
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/appointment_type.xml',
        'demo/crm_lead.xml',
        'demo/hr_employee.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/mail_activity.xml',
        'demo/timesheet.xml',
        'demo/project_project.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_partner/static/src/js/my_tour.js',
        ]
    },
    'author': 'Odoo S.A.',
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
}
