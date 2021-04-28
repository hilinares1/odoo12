{
    "name": "Stock Card",
    "version": "12.1.0.0.0",
    "category": 'Inventory',
    "author": "Falinwa Limited",
    'website': 'https://falinwa.com',
    "category": "Warehouse",
    "description": """\
Manage
======================================================================

* this module to display stock card per item per Warehouse
""",
    "depends": [
        "mail", "stock_account",
    ],
    "data": [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "view/menu.xml",
        "view/stock_card.xml",
        "view/stock_summary.xml",
        "report/stock_card.xml",
    ],
    "installable": True,
    "auto_install": False,
}
