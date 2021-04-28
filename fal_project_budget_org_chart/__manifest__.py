# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Falinwa Project Budget Org Chart',
    'category': 'Accounting & Finance',
    'version': '12.1.0.0.0',
    'description':
        """
Org Chart Widget for falinwa project budget
=======================

This module extend the project budget form with a organizational chart.
(N+1, N+2, direct childerns)
        """,
    'depends': ['fal_project_budget'],
    'data': [
        'views/fal_project_budget_org_templates.xml',
        'views/fal_project_budget_views.xml'
    ],
    'qweb': [
        'static/src/xml/fal_project_budget_org_chart.xml',
    ]
}
