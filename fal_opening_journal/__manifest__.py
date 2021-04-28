#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Falinwa Opening Journal',
    'category': 'Accounting',
    'summary': "Opening Journal Report in CSV File",
    'author': "Falinwa Limited",
    'depends': ['account'],
    'data': [
        'wizard/fal_account_fec_view.xml',
        'data/res_country_data.xml',
        'views/account.xml',
    ],
    'auto_install': False,
}
