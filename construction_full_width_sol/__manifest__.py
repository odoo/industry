{
    'name': 'Construction: Full Width Sales Order Lines',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'depends': [
        'base_industry_data',
        'construction',
        'web_studio',
    ],
    'data': [
        'data/ir_ui_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_full_width_sol/static/src/scss/sale_order.scss',
        ],
    },
    'cloc_exclude': [
        'static/src/scss/sale_order.scss',
    ],
    'license': 'OEEL-1',
    'author': 'Odoo S.A.',
}
