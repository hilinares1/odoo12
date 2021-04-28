# -*- coding: utf-8 -*-
{
    'name': "Document Relation to Object",

    'summary': """
        Falinwa module to attach document to record""",

    'description': """
    Attach document to any record
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Others',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['documents'],

    # always loaded
    'data': [
        'views/ir_attachment.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
