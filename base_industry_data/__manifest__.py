{
    'name': 'Industry base',
    'author': 'Odoo S.A.',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'description': """Base module for data/demo in industries.""",
    'depends': [
        'base',
        'digest',
    ],
    'data': [
        'data/knowledge_tour.xml',
        'data/res_partner_category.xml',
    ],
    'demo': [
        'demo/res_config_settings.xml',
        'demo/res_users.xml',
        'demo/res_partner.xml',
        'demo/res_partner_category.xml',
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
