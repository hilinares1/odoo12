# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Parent Project",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Project',
    'summary': 'Project Parent',
    "description": """
    Module to give parent on project
    """,
    "depends": [
        'project',
        'web_hierarchy',
        'fal_parent_account',
    ],
    'summary': "Project Hierarchial Structure",
    'data': [
        'views/project_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
