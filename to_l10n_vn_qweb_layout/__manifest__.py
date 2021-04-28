{
    'name': "Vietnam QWeb Layouts",

    'summary': """
Accounting QWeb Layouts for companies based in Vietnam
""",

    'description': """

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'support': 'support@ma.tvtmarine.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'l10n_vn'],

    # always loaded
    'data': [
        'views/ir_actions_report_views.xml',
        'views/accounting_external_header_left_layout.xml',
        'views/accounting_external_footer_layout.xml',
        'views/accounting_external_layout_standard.xml',
        'views/accounting_external_layout_c200.xml',
        'views/report_common_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
