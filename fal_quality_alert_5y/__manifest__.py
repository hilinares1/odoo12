{
    'name': 'Fal Quality Alert 5Y',
    'version': '12.2.0.0.0',
    'summary': '5 Why on Quality Alert',
    'author': 'Falinwa Limited',
    'description': '''
        5 Why on Quality Alert.
    ''',
    'depends': [
        'fal_quality_ext',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/fal_quality_alert_5y_report.xml',
        'views/fal_quality_alert_5y_view.xml',
        'views/quality_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
