# -*- coding: utf-8 -*-
{
    "name": "Contract Conditions Invoice",
    "version": "12.1.0.0.0",
    "author": "Falinwa Limited",
    'summary': "add Contract Conditions template on invoice",
    'category': 'Invoicing Management',
    "description": """
    Module to add Contract Conditions template.
    """,
    "depends": ["fal_contract_conditions", 'account'],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "css": [],
    "installable": True,
    "active": False,
    "application": True,
}
