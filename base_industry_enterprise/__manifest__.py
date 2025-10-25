{
    'name': 'Industry Enterprise Base',
    'version': '1.0',
    'category': 'Hidden/Tools',
    'summary': 'Enterprise-level features and modern design system for Mozin Conceito industries',
    'description': """
        Enterprise Base Module for Mozin Conceito Industries
        ======================================================
        
        This module provides:
        * Modern, responsive design system
        * Enterprise-level UI components
        * Advanced dashboard and analytics framework
        * Enhanced security and audit features
        * Performance optimizations
        * Accessibility compliance (WCAG 2.1)
        * Comprehensive documentation framework
        * Reusable component library
    """,
    'author': 'Mozin Conceito',
    'depends': [
        'base',
        'web',
        'web_enterprise',
    ],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'base_industry_enterprise/static/src/scss/enterprise_theme.scss',
            'base_industry_enterprise/static/src/scss/dashboard.scss',
            'base_industry_enterprise/static/src/scss/components.scss',
            'base_industry_enterprise/static/src/js/enterprise_core.js',
            'base_industry_enterprise/static/src/js/dashboard_widgets.js',
            'base_industry_enterprise/static/src/js/analytics_engine.js',
            'base_industry_enterprise/static/src/js/tour_framework.js',
        ],
        'web.assets_frontend': [
            'base_industry_enterprise/static/src/scss/frontend_enterprise.scss',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
