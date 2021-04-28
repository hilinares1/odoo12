# -*- coding: utf-8 -*-
{
    'name': "Inagro Koordinasi Marketing",

    'summary': """
        rayci232@gmail.com""",

    'description': """
        -
    """,

    'author': "INAGRO",
    'website': "https://www.inagro.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','base'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/koordinasi_marketing.xml',
        # 'views/room.xml',
        'views/form_koordinasi.xml',
        'views/info_facilities.xml',
        'views/info_activities.xml',
        'report/mk_report.xml',
        'views/master_facilites.xml',
        'views/master_activities.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}