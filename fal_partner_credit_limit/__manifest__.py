# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Fal Partner Credit Limit",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Sales',
    'summary': 'Partner Credit Limit',
    "description": """
        Module to give Credit Limit feature on partner.
        Credit Limit will be based on 2 parameter
        1. Total Number
        2. Aged Credit
        3. Both
    """,
    "depends": [
        'fal_sale_approval',
    ],
    'data': [
        # "wizard/sale_proposal_wizard_views.xml",
        "views/partner_view.xml",
    ],
    'installable': True,
    'active': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
