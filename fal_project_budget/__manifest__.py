# -*- coding: utf-8 -*-
{
    'name': 'Controlling',
    'version': '12.1.0.0.0',
    'category': 'Accounting & Finance',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'description': """
        ### This module only support for Odoo Enterprise. ###

        Controlling module for analytic account.

    """,
    # We depends on sale and purchase, possibly with timesheet as there is no function if we don't have sale / purchase to control
    'depends': [
        'account_budget',
        'account_accountant',
        'fal_parent_account',
        'fal_multicurrency_group',
        'sale',
        'purchase',
        'hr',
    ],
    'data': [
        'data/fal_project_budget_tags_data.xml',
        'data/project_budget_data.xml',
        'wizard/fal_project_budget_revision_wizard_view.xml',
        'wizard/fal_project_budget_fill_t0_view.xml',
        'wizard/fal_template_budget_fill_data_view.xml',
        'security/ir.model.access.csv',
        'views/fal_project_budget_view.xml',
        'views/product_category_views.xml',
        'views/project_view.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
