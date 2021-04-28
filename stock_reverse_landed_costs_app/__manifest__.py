# -*- coding: utf-8 -*-
{
    "name" : "Reset and Cancel Landed Cost in Odoo",
    "author": "Edge Technologies",
    "version" : "12.0.1.0",
    "category" : "Warehouse",
    'summary': """App for Reverse/Cancel WMS Landed Costs""",
    "description": """
                App for Reverse/Cancel WMS Landed Costs
                cancel stock landed cost on odoo, reset stock landed cost, reset landed cost on odoo Stock landed cost cancel
                landed cost cancel and reset, warehouse landed cost cancel. Cancel Warehouse landed cost. landed cost Reverse
                cancel done landed cost, correct landed cost, ractify landed cost correct done landed cost, ractify done landed cost
                stock landed cost revert stock landed cost odoo freight cost cancel odoo freight cost reverse freight landed cost cancel landed frieght cost in Odoo
                
                """,
    "license" : "OPL-1",
    "price": '25',
    "currency": 'EUR',
    "depends" : ['stock_landed_costs', 'account_cancel'],
    "data": [
        'views/stock_landed_cost_views.xml',
     ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/J6jr2qpS4FM',
    "images":['static/description/main_screenshot.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
