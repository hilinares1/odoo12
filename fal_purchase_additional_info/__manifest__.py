# -*- coding: utf-8 -*-
{
    'name': "Purchase Order : Title, Contact, Attachment, Archive",

    'summary': """
        Purchase Order : Title, Contact, Attachment, Archive""",

    'description': """
        Purchase Order : Title, Contact, Attachment, Archive
        ChangeLog :
        12.1.0.0.0 - Initial Release
        12.4.0.0.0 - Add Purcahse Person in addition to Purchase Representative
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchases',
    'version': '12.4.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['fal_purchase_discount', 'fal_invoice_additional_info'],

    # always loaded
    'data': [
        'views/purchase_views.xml',
        'views/purchase_order_line_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
