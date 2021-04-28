# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Warning Message Management for MRP",
    "version": "12.2.0.0.0",
    "description": """
        This module contains warning message \
        management for manufacturing process management
    """,
    "author": "Falinwa Limited",
    "website": "http://falinwa.com",
    "depends": [
        'fal_finished_product_sequence',
    ],
    "category": "Manufacturing",
    "data": [
        "security/ir.model.access.csv",
        "views/fal_warning_message_view.xml",
        "views/mrp_view.xml",
    ],
    "installable": True
}
