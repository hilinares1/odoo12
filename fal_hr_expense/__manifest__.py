# -*- coding: utf-8 -*-
{
    "name": "HR Expense",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resource',
    'summary': 'Enhance Employee Expense',
    "description": """
        Expense extension

        12.0.1.0.0 - Initial Release
    """,
    "depends": [
        'hr_expense',
    ],
    'data': [
        'data/sequence.xml',
        'views/product_expense_inherit_view.xml',
        'security/ir.model.access.csv',
        'security/fal_hr_expense_security.xml',
        'views/hr_expense_inherit_view.xml',
        'views/hr_expense_sheet_inherit_view.xml',
        'wizard/fal_group_expense_sheet_wizard_view.xml',
        'views/account_inherit_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
