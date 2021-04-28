# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Falinwa Validation process",
    "summary": "Validation process addon",
    "version": "12.0.0.1",
    "category": "",
    "website": "https://falinwa.cn",
    "description": """
		Backend addon for Odoo 12.0
    """,
    "author": "Falinwa",
    "license": "LGPL-3",
    "depends": [
        'web',
        'mail'
    ],
    "data": [
        "security/ir.model.access.csv",
        'views/assets.xml',
        'views/fal_vprocess.xml',
        'views/fal_vprocess_step.xml',
        'views/fal_vprocess_rule.xml',
        'views/fal_vprocess_execution.xml',
        'views/ir_filters.xml',
    ],
    'installable': True,
    'application': True
}
