# -*- coding: utf-8 -*-
# Copyright 2015-today Geo Technosoft (<http://www.geotechnosoft.com>)

{
    'name': 'GTS Aged Partner Pivot Report',
    'summary': 'Aged Pivot Report Odoo',
    'author': 'Geo Technosoft',
    'website': 'http://www.geotechnosoft.com',
    'category': 'Accounting',
    'version': '12.0.0.1',
    'description': """
        This module provide feature to view Aged Partner Balance report in pivot view in odoo.
        Aged Partner Report odoo , Aged Report Financial report , Aged Receivable report , 
        Aged Payable report
    """,
    'sequence': 2,
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/aged_receivable_wiz_view.xml',
        'wizard/aged_payable_wiz_view.xml',
        'wizard/bank_report_wiz_view.xml',
        'report/aged_receivable_report_view.xml',
        'report/aged_payable_report_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'price': 19.00,
    'currency':'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
