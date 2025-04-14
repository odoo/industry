{
    'name': 'Industry base',
    'author': 'Odoo S.A.',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'description': """Base module for data/demo in industries.""",
    'depends': ['base'],
    'data': [
        'data/knowledge_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
    ],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'base_industry_data/static/src/js/my_tour.js',
        ],
    },
    'cloc_exclude': [
        'static/src/js/my_tour.js',
    ],
}
