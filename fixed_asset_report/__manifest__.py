# pylint: disable=missing-docstring, manifest-version-format
# pylint: disable=manifest-required-author
{
    'name': 'Fixed Asset Report',
    'summary': 'Account Fixed Asset PDF Report',
    'author': "Hashem Aly, CORE B.P.O",
    'website': "http://www.core-bpo.com",
    'category': 'accountant',
    'version': '12.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'account_asset',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'data/ir_sequence.xml',
        'wizard/fixed_asset_report_wizard.xml',
        'report/fixed_asset_register_report.xml',
        'report/fixed_asset_schedule_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
