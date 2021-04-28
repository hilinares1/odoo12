# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "HRD-08_Payroll China Falinwa",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    "description": """
    Module to developed Odoo payroll based on Falinwa standard.
    """,
    "depends": ['fal_payroll_engine'],
    'init_xml': [],
    'data': [
        'report/hr_payroll_report_view.xml',
        'data/base_data.xml',
        'data/hr_payroll_report.xml',
    ],
    'css': [],
    'js': [
    ],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}

