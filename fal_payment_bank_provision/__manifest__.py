# -*- coding: utf-8 -*-
{
    "name": "Payment Bank Provision",
    "version": "12.1.0.0.0",
    'category': 'Accounting & Finance',
    "author": "Falinwa Limited",
    'website': 'https://falinwa.com',
    "description": """
    Module to add payment bank provision
    """,
    "depends": [
        "account",
        "sale_management",
        "purchase",
        "fal_multi_payment_wizard"],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",
        "data/account_data.xml",
        "data/provision_journal_data.xml",
        "wizard/fal_multi_payment_wizard_view.xml",
        "views/bank_provision_view.xml",
        "views/account_journal_view.xml",
    ],
    "active": False,
    "application": False,
    "installable": True,
}
