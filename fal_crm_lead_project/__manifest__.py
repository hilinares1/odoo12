# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'CRM: Opportunity to Project',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Indonesia',
    'description': '''
    This module has features:\n
    1. Create project from Opportunity\n
    ''',
    'depends': [
        'sale_crm',
        'sale_timesheet',
        'project',
    ],
    'data': [
        'views/crm_lead_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
