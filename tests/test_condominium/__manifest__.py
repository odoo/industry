{
    'name': 'test condominium industry',
    'version': '1.0',
    'category': 'Hidden/Tests',
    'description': """A module to test Condominium business flows.""",
    'depends': ['base'],
    'assets': {
        'web.assets_tests': [
            'test_condominium/static/src/**/*',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}
