# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': "Customer Invoice and Vencor Bills Relation",
    'summary': """
        Make A link between Customer Invoice and Vendor Bills""",
    'description': """
        Sometimes corporation are working by using 3rd party supplier. That's why we want to connect customer invoice and vendor bills to know the relation between the 2 records.
    """,
    "version": "12.4.0.0.0",
    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'wizard/account_invoice_line_add_aci_wizard_view.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
