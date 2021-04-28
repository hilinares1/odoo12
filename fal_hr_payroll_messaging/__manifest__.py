# -*- coding:utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payroll Messaging',
    'version': '12.4.0.0.0',
    'category': 'Human Resources',
    'description': '''
        Module to add message in Employee Payslip

        Changelog:
        12.4.0.0.0 - Initial Release
    ''',
    'author': 'Falinwa Limited',
    'website': 'http://www.falinwa.com',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
