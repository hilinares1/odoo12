# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Minimum Sale",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Sales',
    'summary': 'Add Minimum Sales Price feature in sales order',
    "description": """
    Module to give minimum sales price in sales order.
    """,
    "depends": [
        'product',
        'fal_sale_approval'
    ],
    'data': [
        "views/product_pricelist_view.xml",
        "views/sale_views.xml",
        # "wizard/sale_proposal_wizard_views.xml"
    ],
    'installable': True,
    'active': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
