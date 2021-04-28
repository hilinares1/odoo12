# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': "Holiday Leaves Overlap",
    'summary': """Handle leaves overlap""",
    'author': 'Falinwa Limited,Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'http://falinwa.com',
    'category': 'Human Resources',
    'version': '12.0.1.0.0',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays.xml'
    ],
    'installable': True,
}
