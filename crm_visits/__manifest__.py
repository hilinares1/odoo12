# -*- coding: utf-8 -*-
{
    'name': "Visits",
    'summary': """
        Track activities""",
    'website': 'https://github.com/kmcalda/crm_visits',
    'author': "Kevin Marvin Calda",
    'category': 'Extra tool',
    'version': '0.1',
    'license': 'AGPL-3',
    'sequence': 10,
    'depends': [
        'crm',
        'sale_management',
        'contacts',
    ],
    'data': [
        'views/visit_view.xml',
        'views/custom_views.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    'installation': True,
    'auto_install': False,
}