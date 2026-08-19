{
    'name': 'Property Listing',
    'version': '1.1',
    'category': 'Services',
    'author': 'Odoo S.A.',
    'depends': [
        'sale_crm',
        'web_studio',
        'website_crm',
        'website_sale',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/crm_team.xml',
        'data/product_public_category.xml',
        'data/ir_default.xml',
        'data/website_view.xml',
        'data/website_page.xml',
        'data/website_theme_apply.xml',
        'data/website.xml',
    ],
    'demo': [
        'demo/website/website.xml',
    ],
    'license': 'OEEL-1',
    'cloc_exclude': [
        'data/website_view.xml',
    ],
    'images': ['images/main.png'],
}
