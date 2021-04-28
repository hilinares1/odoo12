# -*- coding: utf-8 -*-
{
    'name': "Financial Report - Total on Group-by",

    'summary': """
        Module to add total on groupby function on financial report""",

    'description': """
        On Financial Report, if you make filter (group-by). You will not get the Total.
        This module add Total for each year / comparison by year
    """,

    'author': "CLuedoo",
    'website': "https://cluedoo.com",
    'category': 'Accounting & Finance',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account_reports'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [
    ],
}
