# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and
# licensing details.
{
    'name': 'Falinwa Intercompany Analytic Account Behaviour',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'description': """
Module to give analytic account behaviour based on Falinwa expected for intercompany.

Enterprise Only

    Changelog:
        V.12.0.1.0.0 - First Release
    """,
    'depends': [
        'fal_analytic_account_ext', 'inter_company_rules'
    ],
    'data': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
