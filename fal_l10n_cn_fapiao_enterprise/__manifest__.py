# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'China - Fapiao for Enterprise',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://www.falinwa.com',
    'category': 'Accounting & Finance',
    'summary': 'Move Fapiao menu correctly.',
    'description': """
Fapiao menu are not moved to correct accounting module on Enterprise. This module move it.
""",
    'depends': ['l10n_cn_fapiao', 'account_accountant'],
    'data': [
        'views/fapiao_view.xml',
    ],
}
