# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'China - Accounting',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://www.falinwa.com',
    'category': 'Localization',
    'summary': 'Manage the accounting chart (with hierarchy) for China',
    'description': """
This is the module to manage
the accounting chart (with hierarchy) for China in Odoo.
(China COA)
""",
    'depends': ['account_accountant','account_check_printing'],
    'data': [
        'data/account_chart_type.xml',
        'data/account_chart_general_business_template.xml',
        'data/account_tax_template.xml',
    ],
}
