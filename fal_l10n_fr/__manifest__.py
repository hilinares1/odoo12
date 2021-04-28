# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'French Accounting',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Localization',
    'summary': 'Manage the accounting chart (with hierarchy) for France',
    'description': """
This is the module to manage the accounting chart (with hierarchy) for France in Odoo.

This module applies to companies based in France mainland.
It doesn't apply to companies based in the DOM-TOMs
(Guadeloupe, Martinique, Guyane, Réunion, Mayotte).

This localisation module creates the VAT taxes of type
'tax included' for purchases
(it is notably required when you use the module 'hr_expense').
Beware that these 'tax included' VAT taxes are not managed
by the fiscal positions provided by this
module (because it is complex to manage both 'tax excluded'
and 'tax included' scenarios in fiscal positions).

This localisation module doesn't properly handle the scenario
when a France-mainland company sells services to a company
based in the DOMs. We could manage it in the fiscal positions,
but it would require to differentiate between 'product' VAT taxes
and 'service' VAT taxes. We consider that it is too 'heavy'
to have this by default in l10n_fr;
companies that sell services to DOM-based companies should update the
configuration of their taxes and fiscal positions manually.

**Credits:** Sistheo, Zeekom, CrysaLEAD,
Akretion, Falinwa Limited, and Camptocamp.
""",
    'depends': ['base_iban', 'base_vat', 'fal_parent_account',],
    'data': [
        'data/fal_account_account_template.xml',
        'data/account_data.xml',
        'data/account_tax_data.xml',
    ],
}
