{
    'name': 'Construction Line Numbering',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'author': 'Odoo S.A.',
    'depends': [
        'base_industry_data',
        'construction',
        'sale_management',
        'web_studio',
    ],
    'data': [
        'data/ir_ui_view.xml',
        'data/qweb_view.xml',
    ],
    'license': 'OPL-1',
    'cloc_exclude': [
        'data/qweb_view.xml',
    ],
    'website': "https://www.odoo.com/all-industries",
}
