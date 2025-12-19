# -*- coding: utf-8 -*-
{
    'name': 'OSUS Sales & Invoicing Dashboard',
    'version': '17.0.2.0.0',
    'category': 'Sales',
    'summary': 'Real-time sales pipeline, invoicing, and collection analytics',
    'description': '''
        Enterprise Sales & Invoicing Dashboard
        ========================================
        * Real-time KPI tracking (8 key metrics)
        * Interactive Chart.js visualizations (6 charts)
        * Multi-dimensional filtering (7 independent filters)
        * Detailed analysis tables (4 breakdowns)
        * CSV data export (4 report types)
        * Commission tracking for internal agents
        * Invoice aging analysis by due date buckets
        * Mobile-responsive Bootstrap 5 layout
    ''',
    'author': 'OSUS Properties',
    'license': 'LGPL-3',
    'depends': ['sale', 'account', 'le_sale_type', 'website', 'commission_ax'],
    'assets': {
        'web.assets_backend': [
            # Chart.js from CDN (with fallback to local in JS)
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
            # Custom assets
            'osus_sales_invoicing_dashboard/static/src/xml/dashboard_charts.xml',
            'osus_sales_invoicing_dashboard/static/src/js/dashboard_charts.js',
            'osus_sales_invoicing_dashboard/static/src/js/dashboard_filters.js',
            'osus_sales_invoicing_dashboard/static/src/scss/dashboard_charts.scss',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/dashboard_security.xml',
        'views/website_layout_fix.xml',
        'views/dashboard_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
