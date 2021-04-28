{
    "name": "Payroll Accounting Enhancement",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'sequence': 50,
    'category': 'Human Resources',
    'summary': 'This module add HR Payroll functionality',
    'website': 'https://falinwa.com',
    "description": """
        Module to extends Payroll Accounting
    """,
    "depends": [
        'hr_payroll_account',
        'hr_expense'
    ],
    'data': [
        'views/hr_payroll_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
