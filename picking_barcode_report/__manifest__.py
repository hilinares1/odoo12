# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Geminate Consultancy Services (<http://geminatecs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
	'name': 'Print Picking Barcode Labels',
	"version": "12.0.3",
	'author': 'Geminate Consultancy Services',
	'category': 'stock',
	'website': 'https://www.geminatecs.com',
	'description': '''Print Picking Barcode Labels''',
	'depends': ['stock', 'dynamic_barcode_labels'],
	'data': [
		'views/menu_view.xml',
		'security/ir.model.access.csv',
		'wizard/picking_barcode_labels.xml',
		'views/picking_labels_report.xml',
		'views/picking_barcode_labels.xml',
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
