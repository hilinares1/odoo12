# encoding: utf-8
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'MRP Enhancement',
    'version': '12.2.0.0.0',
    'author': 'Falinwa Limited',
    'category': 'Manufacturing',
    'summary': 'This module add MRP functionality',
    'website': 'https://falinwa.com',
    'description': '''
    This module has features:\n
    1. Split Workorders dashboard into 2 button, WO Ready and WO in Progress.\n
    2. Workcenter / Workorders access right for specific Users - Manager.\n
    3. User can only see Dashboard on MRP. No more Operations\PLanning\Master Data\Reporting.\n
    ''',
    'depends': [
        'mrp_workorder',
        'fal_finished_product_sequence',
    ],
    'data': [
        'security/workcenter_security.xml',
        'views/fal_production_order.xml',
        'views/mrp_views.xml',
        'views/mrp_views_menus.xml',
        'views/mrp_workcenter_views.xml',
        'views/mrp_workorder_views.xml',
        'views/res_users_view.xml',
        'wizard/multi_check_stock_mrp_view.xml',
        'wizard/multi_cancel_production_view.xml',
        'report/mrp_po_reserved_templates.xml',
        'report/mrp_report_views_main.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
