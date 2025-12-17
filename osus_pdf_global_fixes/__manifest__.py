# -*- coding: utf-8 -*-
{
    'name': 'OSUS PDF Global Fixes',
    'version': '17.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Professional PDF Report Styling and Layout Fixes',
    'description': '''
        Global PDF Report Enhancements:
        - Professional, clean, and clear PDF formatting
        - Fixed content overflow and overlapping issues
        - Optimized page breaks
        - Enhanced typography and spacing
        - High-quality DPI settings
        - Consistent margins and layout across all reports
    ''',
    'author': 'OSUS Properties',
    'website': 'https://osusproperties.com',
    'depends': ['base', 'web'],
    'data': [
        'views/report_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'osus_pdf_global_fixes/static/src/css/report_styles.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
