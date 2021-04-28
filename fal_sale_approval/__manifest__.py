# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Sale Approval",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Sales',
    'summary': 'Sales Approval',
    "description": """
        Add Waiting Approval stages on sales order. There is 2 option available:
        1. Always using proposal
        2. Can skip the proposal process
    """,
    "depends": [
        'sale_management',
    ],
    'data': [
        "views/sale_views.xml",
        # "wizard/sale_proposal_wizard_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
