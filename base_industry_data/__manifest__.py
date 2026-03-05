{
    'name': 'Industry base',
    'version': '1.2',
    'author': 'Odoo S.A.',
    'category': 'Hidden/Tools',
    'depends': [
        'base',
        'digest',
        'hr',
        'knowledge',
    ],
    'data': [
        'data/knowledge_tour.xml',
        'data/res_partner_category.xml',
    ],
    'demo': [
        'demo/hr_employee.xml',
        'demo/ir_cron.xml',
        'demo/res_users.xml',
        'demo/res_partner.xml',
        'demo/res_partner_category.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'base_industry_data/static/src/js/my_tour.js',
        ],
    },
    'cloc_exclude': [
        'static/src/js/my_tour.js',
    ],
}
