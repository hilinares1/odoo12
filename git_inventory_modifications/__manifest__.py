{
    'name' : 'GIT Inventory Date Field Modifications To Editable',
    'version' : '12.0',
    'summary': 'modify date field to make it editable',
    'description': """
        date field in odoo is readonly field by default nd user can't edit or change it this module customize this field to make it editable by users
    """,
    'category': 'software services',
    'website': 'http://www.git-eg.com',
    'depends' : ['stock'],
    'data': [

        'views/views.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
    'application':True
}
