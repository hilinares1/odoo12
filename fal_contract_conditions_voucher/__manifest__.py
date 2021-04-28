# -*- coding: utf-8 -*-
{
    "name": "Contract Conditions Voucher",
    "version": "12.2.1.0.0",
    "author": "Falinwa Limited",
    'category': "Accounting",
    'summary': "add Contract Conditions template on Account Voucher",
    "description": """
    Module to add Contract Conditions template.
    """,
    "depends": ["fal_contract_conditions", "account_voucher"],
    "data": [
        "views/account_voucher_view.xml",
    ],
    "css": [],
    "installable": True,
    "active": False,
    "application": True,
}
