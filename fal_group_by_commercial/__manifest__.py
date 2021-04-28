# -*- coding: utf-8 -*-

{
    'name': 'Group By Commercial',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Limited',
    'category': 'Sale',
    'website': 'www.falinwa.com',
    'description': '''
        Module to define group by Commercial Partner on
        Sale/Purchase(Quotation,Order), Invoice/Payment(Supplier,Customer).
    ''',
    'depends': [
        'sale',
        'purchase',
        'account_voucher'
    ],
    'init_xml': [],
    'data': [
        'views/account_invoice_view.xml',
        'views/account_voucher_view.xml',
        'views/purchase_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml'
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
