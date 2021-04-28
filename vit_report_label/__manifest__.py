# -*- coding: utf-8 -*-
{
    'name': "vit_report_label",

    'summary': """
        Label""",

    'description': """
        Print Label Package
    """,

    
    'author': 'yusup[vitraining.com]',
    'website': 'http://www.vitraining.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/paperformat.xml',
        'report/file.xml',
        'report/file_layout.xml',
    ],
}