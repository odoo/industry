{
    'name': 'Photography',
    'version': '1.0',
<<<<<<< 875a02bf3c018b60fc4273a15eb87b232b13bfd4
    'category': 'Services',
||||||| e5a1ba433a012ad0dcff740c631f8f97783d2861
    'category': 'Services',
    'description': """
        The Odoo app for photography professionals provides a preconfigured database with all the
        necessary features to manage their business. The app includes pre-configured products and
        projects, a website template, and beautiful quotes to help photographers showcase their work
        and attract new clients. With this app, photographers can easily manage their projects, track
        their time, and create invoices. The website template allows photographers to showcase their
        portfolio and services, and the pre-configured products make it easy to sell prints and other
        photography-related items.
    """,
=======
    'category': 'Culture and Arts',
    'description': """
        The Odoo app for photography professionals provides a preconfigured database with all the
        necessary features to manage their business. The app includes pre-configured products and
        projects, a website template, and beautiful quotes to help photographers showcase their work
        and attract new clients. With this app, photographers can easily manage their projects, track
        their time, and create invoices. The website template allows photographers to showcase their
        portfolio and services, and the pre-configured products make it easy to sell prints and other
        photography-related items.
    """,
>>>>>>> 20014fd4a7f3eef3b4149c7cb00d24f3495f074a
    'depends': [
        'crm',
        'documents_project',
        'knowledge',
        'project_enterprise',
        'sale_management',
        'sale_project',
        'sign',
        'website_appointment',
    ],
    'data': [
        'data/res_groups_data.xml',
        'data/mail_templates.xml',
        'data/project_data.xml',
        'data/product_data.xml',
        'data/appointment_data.xml',
        'data/sale_order_template_data.xml',
        'data/crm_tags_data.xml',
        'data/ir_attachment.xml',
        'data/documents_folder.xml',
        'data/sign_template.xml',
        'data/sign_item.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
        'data/website_view.xml',
        'data/website_theme_apply.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/crm_lead.xml',
        'demo/appointment_data.xml',
        'demo/sale_order.xml',
        "demo/sale_order_confirm.xml",
        'demo/project_task.xml',
        'demo/documents_folder.xml',
        'demo/appointment.xml',
        'demo/website_ir_attachment.xml',
        'demo/website_view.xml',
        "demo/website_theme_apply.xml",
        'demo/website_page.xml',
        'demo/website_menu.xml',
        "demo/website.xml",
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'photography/static/src/js/my_tour.js',
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
}
