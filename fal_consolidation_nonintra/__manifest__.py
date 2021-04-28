# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Consolidation Non Intra",
    "version": "12.3.0.0.0",
    "author": "Falinwa",
    "description": """
    Module to filter non intra on acconting reports
    """,
    "depends": [
        'account_reports',
    ],
    'init_xml': [],
    'data': [
        'data/data.xml',
        'views/financial_report_view.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
