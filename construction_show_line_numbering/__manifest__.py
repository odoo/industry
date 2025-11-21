{
    'name': 'Construction Show Line Numbering',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'author': 'Odoo S.A.',
    'depends': [
        'construction_line_numbering',
        'sale_management',
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
