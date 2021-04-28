# -*- coding:utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payroll and Supplier Payment Email',
    'version': '12.4.0.0.0',
    'category': 'Human Resources',
    'description': '''
        Module to add button SendbyEmail in Employee Payslip , and button SendbyEmail in Accounting Payment
    ''',
    'author': 'Falinwa Limited',
    'website': 'http://www.falinwa.com',
    'depends': [
        'hr_payroll','mail'
    ],
    'data': [
        'views/sendemail.xml',
        'data/emailtemplate.xml',
        'security/fal_hr_payroll_security.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
