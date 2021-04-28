{
    'name': "Falinwa Credit Limit Formula",
    'version': '1.0',
    'author': "Falinwa Limited",
    'category': 'Sales',
    'description': """
    To control the customer credit limit.
    """,
    # data files always loaded at installation
    'depends': [
        'fal_partner_credit_limit',
        'purchase',
        'sale',
        #'fal_multicurrency_group'
    ],
    'data': [
        # 'views/*.xml',
        'views/partner_view.xml',
        'wizard/fal_alert_wizard_view.xml',
    ],
}
