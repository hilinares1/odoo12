# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "PJC-02_Project Extension",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    "description": """
     Project for final customer Level1:
     the name and the whole project is defined by the car company usually. 1 project can have only 1 final customer Level1 and several final customer Level2 (but not given in OpenERP).
     No need description / details at this level because it’s given at subproject level. and Module for maintain project version
     Subproject for final customer Level2: for 1 project, we can have several subprojects. 1 subproject = 1 final customer Level2.
    """,
    "depends": ['sale', 'purchase', 'project', 'kanban_draggable'],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/task_update_wizard.xml',
        'views/project_view.xml',
        'views/res_partner_view.xml',
        'views/search_view.xml',
        'views/res_config_setting_view.xml',
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
    'js': ['static/src/js/fal_project.js'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
