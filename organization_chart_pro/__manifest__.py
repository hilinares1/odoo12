# -*- coding: utf-8 -*-
{
	'name': "Organization Chart Pro",
	'summary': """Dynamic Display of your Department Chart - Drag and Drop - Search - Add - Edit - Delete - Screenshot""",
	'description': """Dynamic Display of your Department Organization""",
	'author': "SLife Organization",
	'category': 'Human Resources',
	'version': '2.0',
	'license': 'OPL-1',
	'depends': ['hr'],
	'price': 10.00,
	'currency': 'EUR',
	'support': 'frejusarnaud@gmail.com',
	'data': ['views/org_chart_views.xml'],
	'images': [
		'static/src/img/main_screenshot.png'
	],
	'qweb': [
        "static/src/xml/org_chart_department.xml",
    ],
	'installable': True,
	'application': True,
	'auto_install': False,
}
