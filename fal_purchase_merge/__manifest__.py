# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'license': 'LGPL-3',
    "name": "Request for Quotation Merge",
    "version": "12.1.0.0.0",
    "author": "Falinwa Limited",
    'maintainer': "Falinwa Limited",
    'website': 'https://falinwa.com',
    'category': 'Purchases',
    "summary": "Combine multiple RFQ or Purchase Orders",
    'description': """
For Odoo Enterprise Version 9.0, this module supports combining or merging Request for Quotation documents.
When you have multiple requests for the same supplier it can be useful to merge them all into one before creating a Purchase Order and sending.
A new Request for Question with a new reference is generated and the originals are cancelled. This new document contains all the lines and notes from the original separate documents. Merging works if multiple Vendors are selected.
Note: Starting with version 9.0, new procurements are automatically merged with existing Request for Quotations for the same Vendor.  This custom functionality is provided only to handle the use case where manually created Requests for Quotation that need to be merged.

    """,
    "depends": ["purchase_stock"],
    "data": [
        'wizard/purchase_order_group_view.xml',
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
