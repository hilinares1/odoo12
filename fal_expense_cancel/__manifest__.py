{
    'name': 'HRD-03_Expense Cancel',
    'version': '12.1.0.0.0',
    'category': 'Expense Cancel',
    'author': 'Falinwa Limited',
    'summary': 'Expense Cancel',
    'description': """
Expenses Cancel:
===========================
Allows you to cancel an expense already paid to return to draft state and make
changes to your entrie or regenerate

    """,
    'depends': ['base', 'account', 'hr_expense', 'account_cancel'],
    'data': [
        'views/hr_expense_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

