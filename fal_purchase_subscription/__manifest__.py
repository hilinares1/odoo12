# -*- coding: utf-8 -*-
{
    'name': "Purchase Subscription",
    'summary': """
        module to recurring purchase order""",

    'description': """
        module to recurring purchase order
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Purchases',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'views/subscription_view.xml',
        'wizard/purchase_subscription_wizard_view.xml',
        'data/purchase_contract_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
