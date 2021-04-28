{
    "name": "Fal Quality Alert 5M",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Manufacturing',
    'summary': '5 How on Quality Alert',
    'website': 'https://falinwa.com',
    "description": """
        5M on Quality Alert.
    """,
    "depends": [
        'fal_quality_ext',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/fal_quality_alert_5m_report.xml',
        'views/fal_quality_alert_5m_view.xml',
        'views/quality_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
