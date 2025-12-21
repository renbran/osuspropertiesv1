{
    'name': 'OSUS Invoice Report - Enhanced with Smart Payment Vouchers',
    'version': '17.0.3.3.0',
    'summary': 'Professional UAE Tax Invoice Reports with Intelligent Payment Vouchers',
    'description': '''
        Professional Tax Invoice Reports with Advanced Features - Now Default for Accounting
        =================================================================================
        
        🎯 DEFAULT ACCOUNTING REPORTS OVERRIDE
        =====================================
        This module now automatically becomes the default for ALL invoice and bill printing in Odoo:
        - Customer Invoices: Use enhanced invoice template with professional formatting
        - Vendor Bills: Use simplified bill template optimized for vendor payments
        - Smart Auto-Detection: Automatically chooses correct template based on document type
        
        ✨ ENHANCED INVOICE FEATURES
        ==========================
        - UAE VAT compliant invoice layout
        - Real estate commission specific fields
        - UK date format support
        - Amount in words conversion
        - Professional styling with Bootstrap 5
        - Multi-company support
        - Inheritance-safe implementation
        
        💡 SMART BILL TEMPLATE
        ======================
        - Simplified structure optimized for vendor bills
        - Default Odoo table structure and dates maintained
        - Professional formatting similar to invoice template
        - Automatic vendor/customer detection
        - Consistent styling across all document types
        
        🔧 TECHNICAL IMPROVEMENTS
        =========================
        - Overrides default Odoo invoice reports automatically
        - Smart template dispatcher based on move_type
        - Enhanced document type detection
        - Improved error handling and fallbacks
        - Professional payment voucher enhancements
        
        NEW: Smart Payment Voucher Enhancements
        =====================================
        - Intelligent document type detection (bills vs invoices)
        - Dynamic label generation ("Related bill" vs "Related invoice")
        - Multiple document support with detailed tables
        - Payment status indicators (full/partial payment)
        - Remaining balance calculations
        - Enhanced document reference formatting
        - Professional summary sections
        - Automatic reconciliation analysis
    ''',
    'category': 'Accounting/Accounting',
    'author': 'OSUS Real Estate',
    'website': 'https://www.osus.ae',
    'depends': ['account', 'base', 'sale', 'portal', 'le_sale_type'],
    'external_dependencies': {
        'python': ['qrcode', 'num2words'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/report_paperformat.xml',
        
        # Views
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/sale_order_views.xml',
        'views/portal_templates.xml',

        
        # Reports
        'report/report_action.xml',
        'report/bill_report_action.xml',
        'report/payment_voucher_report_action.xml',
        'report/override_default_reports.xml',
        'report/smart_dispatcher.xml',
        'report/invoice_report.xml',
        'report/bill_report.xml',
        'report/payment_voucher_report.xml',

        'report/simple_test_report.xml',
    ],
    'demo': [
        'data/demo_payment_data.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ],
        'web.report_assets_pdf': [
            'invoice_report_for_realestate/static/src/css/report_style.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'auto_install': False,
}