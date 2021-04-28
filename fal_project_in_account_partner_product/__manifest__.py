# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Analytic Account in Invoice Partner Product',
    'version': '12.2.0.0.0',
    'author': 'Falinwa Limited',
    'summary': """
        module to add Analytic account from partner or product.""",
    'website': "https://falinwa.com",
    'description': '''
        Module to add Analytic Account from partner or product.
    ''',
    'depends': [
        'fal_project_in_partner_product',
        'fal_analytic_account_ext',
	'fal_account_bank_statement_reconciliation_ext',
    ],
    'init_xml': [],
    'data': [
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,

}
