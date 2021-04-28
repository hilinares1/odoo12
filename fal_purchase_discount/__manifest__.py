# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2014-2017 Tecnativa - Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase order lines with discounts",
    "summary": "add constraint only put discount from 0% to less than 100%, and fix wrong price on stock",
    "author": "Falinwa Limited",
    'website': 'https://falinwa.com',
    "version": "12.1.0.0.0",
    "category": "Purchases",
    "depends": ["purchase_discount", 'purchase_stock'],
    "data": [
    ],
    "license": 'AGPL-3',
    'installable': True,
}
