{
    'name': 'Construction Show Line Numbering',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'author': 'Odoo S.A.',
    'depends': [
        'base_industry_data',
        'construction',
        'construction_line_numbering',
    ],
    'data': [
        'data/ir_ui_view.xml',
        'data/qweb_view.xml',
    ],
    'license': 'OEEL-1',
    'cloc_exclude': [
        'data/qweb_view.xml',
    ],
    'url': "https://www.odoo.com/trial?industry&selected_app=construction",
    'website': "https://www.odoo.com/industries/construction",
}
