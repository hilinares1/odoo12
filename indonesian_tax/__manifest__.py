# -*- coding: utf-8 -*-
{
    'name': 'Indonesian Tax',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Localization',
    'description': '''
    This module has features:\n
    1. Add capability for storing NPWP\n
    2. Faktur Pajak
    ''',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/faktur_pajak.xml',
        'views/invoice_inherit_view.xml',
        'views/partner_views.xml',
        'wizard/generate_faktur_view.xml',
        'report/efaktur_invoice_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
