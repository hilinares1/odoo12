# -*- coding: utf-8 -*-
{
    "name": "Contract Conditions Purchase",
    "version": "12.2.1.0.0",
    "author": "Falinwa Limited",
    'category': 'Purchases',
    'summary': "add Contract Conditions template on purchase order",
    "description": """
    Module to add Contract Conditions template.
    """,
    "depends": ["fal_contract_conditions", 'purchase'],
    "data": [
        "views/purchase_view.xml",
    ],
    "css": [],
    "installable": True,
    "active": False,
    "application": True,
}
