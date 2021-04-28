# -*- coding: utf-8 -*-
{
    'name': "Payment Acquirer: Doku Implementation",
    'version': '12.1.0.0.0',
    'category': 'Accounting',
    'author': 'Falinwa Limited',
    'sequence': 0,
    'summary': 'Payment Acquirer: Doku Implementation',
    'depends': [
        'sale',
        'payment',
        'website_sale',
        'account',
    ],
    'data': [
        'views/payment_views.xml',
        'data/payment_icon_data.xml',
        'views/payment_doku_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/account_invoice_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'qweb': [
    ],
    'website': 'https://falinwa.com',
    'images': ['static/description/icon.png'],
    'support': 'randy.raharjo@falinwa.com'
}
