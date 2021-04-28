# -*- coding: utf-8 -*-
{
    "name": "Deferred Cost",
    "version": "12.3.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Accounting",
    'summary': '',
    "description": """
        Assets on Deferred Cost
    """,
    "depends": ['account_asset'],
    'init_xml': [],
    'data': [
        'wizard/wizard_asset_compute_view.xml',
        'report/account_deferred_cost_report_view.xml',
        'views/account_deferred_cost.xml',
        'views/account_deferred_cost_invoice_view.xml',
        # 'views/account_deferred_cost_product_view.xml',
        # 'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
