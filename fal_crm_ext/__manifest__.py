# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "CRM EXT",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    "description": """
    Module to extend CRM.
    """,
    "depends": [
        'crm',
    ],
    'init_xml': [],
    'data': [
        "security/ir.model.access.csv",
        'data/crm_question.xml',
        'wizard/lost_and_link_partner_crm_wizard_views.xml',
        'views/crm_lead_view.xml',
        'views/utm_view.xml',
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
