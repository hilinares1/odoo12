# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Salesmen manage',
    'author': 'Ziad Monim(elata79@gmail.com)',
    'summary': 'Module for manage salesmen target and discounts',
    'depends': ['sale','sales_team'],
    'category': 'Sales',
    'description': """
        This Module for manage salesmen target and discounts
            * first thing you create salesman configuration from configuration page in sales module, 
                create it with monthly target and discount is available for him to give, if add more 
                than discount available for him so need to ask for approve for the top manager.
            * you need activate the discounts in the sale module settings
            * I add new group as Top manager that the one approve for big discounts or rejected it
            * if rejected and the saleman can contiue negotiate with the customer and set the quotation to
              draft with duplicate or create new one
        """,
    'data': [
        'views/test_view.xml',
        'security/ir.model.access.csv',
        'security/sales_team_security.xml',
    ],
    'images': ['static/description/saleman.gif'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False,
}
