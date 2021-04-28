{
	"name": "Stock Card 12", 
	"version": "1.7",
	"depends": [
		"stock",
		"mrp",
		# "product_expiry",
		# "vit_common",
		# "vit_stock",
	], 
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"website": "www.vitraining.com",
    'category': 'Accounting',
	'images': ['static/description/images/main_screenshot.jpg'],
	'price':'30',
    'currency': 'USD',
	"category": "Warehouse",
	"summary" : "This modul to display stock card per product per Warehouse and product summary per Warehouse",
	"description": """\

Manage
======================================================================

* this modul to display stock card per item per Warehouse
* this modul to display stock card summary per Warehouse
* Add cron to running stock card per item per Warehouse & stock card summary per Warehouse

""",
	"data": [
		"view/stock_card.xml", 
		"view/stock_summary.xml",
		# "view/stock_summary_new_view.xml",
		# "view/stock_summary_detail.xml",
		# "view/stock_inventory_view.xml",
		"menu.xml", 
		# "report/stock_card.xml",
		# "report/report_stock_xlsx_view.xml",
		"data/ir_sequence.xml",
		"security/ir.model.access.csv",
		"data/cron.xml",
	],
	"application": True,
	"installable": True,
	"auto_install": False,
}