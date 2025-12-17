# -*- coding: utf-8 -*-
{
    'name': 'Form Control Buttons',
    'summary': 'Replace icon-only form Save button with plain text "Save" globally',
    'version': '17.0.1.0.0',
    'author': 'Brain Station 23',
    'website': 'https://brainstation-23.com',
    'category': 'Web',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [],
    'images':['static/description/banner.png'],
    'assets': {
        'web.assets_backend': [
            '/form_control_buttons_17_0/static/src/css/save_button_text.css',
            '/form_control_buttons_17_0/static/src/js/save_button_text.js',
        ],
    },
    'installable': True,
    'application': False,
}

