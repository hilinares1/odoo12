# -*- coding: utf-8 -*-
{
    'name': "Customer Check-in",
    'summary': """Now your sales reps can check-in at customers premise and you can track their visits and timming""",
    'Version': '1.0.0',
    'category': 'Sales',
    'description': """
Sales Rep Customer Check-in:
==========================

    * The user  could use check-in button on the Customer form view to record his visit to the Customer.\n
    * Each Sales Rep can see his visits only.\n
    * Sales Manager see all visits.\n

    """,

    'author': "Techno Town",
    'website': "http://www.technotown.technology",
    'support': 'info@technotown.technology',
    'price': 10,
    'currency' : 'EUR',
    'license': 'LGPL-3',
    'images' : ['images/check_screen_shoot.png','images/check_thumb.png'],
    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','sales_team','web','base_geolocalize'],
    'data': [
        'security/ir.model.access.csv',
        'views/new_templates.xml',
        'views/partner_inh.xml',
        'views/customers_vistis_view.xml',
        'security/security_rules.xml'
    ],
    'demo': [
    ],
}