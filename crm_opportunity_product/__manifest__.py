# -*- encoding: utf-8 -*-
{
	"name": "CRM Opportunity Product",
	"version": "12.0",
	"author": "PPTS [India] Pvt.Ltd.",
	"website": "http://www.pptssolutions.com",
	"sequence": 0,
	"depends": [
		"base",'sale_crm','sale','product'
	],
	"category": "Settings",
	"complexity": "easy",
	"description": """
	This module allow to add products on opportunity and create quote with that. 
	""",
	"data": [
		'security/ir.model.access.csv',
		'views/opportunity_product.xml',
	],
	"demo": [
	],
	"test": [
	],
	"auto_install": False,
	"installable": True,
	"application": False,
    'images': ['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
