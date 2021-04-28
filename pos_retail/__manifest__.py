# -*- coding: utf-8 -*-
# License: Odoo Proprietary License v1.0
{
    'name': "POS All In One Futures (Shop & Restaurant)",
    'version': '8.3.0.2.7',
    'category': 'Point of Sale',
    'author': 'TL Technology',
    'live_test_url': 'http://posodoo.com/web/signup',
    'price': '450',
    'website': 'http://posodoo.com/web/signup',
    'sequence': 0,
    'depends': [
        'base',
        'sale_stock',
        'account',
        'account_cancel',
        'pos_restaurant',
        'bus',
        'stock',
        'purchase',
        'product',
        'product_expiry',
    ],
    'demo': ['demo/demo_data.xml'],
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'security/ir_rule.xml',
        'views/pos_menu.xml',
        'reports/pos_lot_barcode.xml',
        'reports/pos_sale_analytic.xml',
        'reports/report_pos_order.xml',
        'reports/pos_sale_report_template.xml',
        'reports/pos_sale_report_view.xml',
        'datas/product.xml',
        'datas/schedule.xml',
        'datas/email_template.xml',
        'datas/customer.xml',
        'datas/res_partner_type.xml',
        'datas/barcode_rule.xml',
        'datas/pos_loyalty_category.xml',
        'datas/stock_picking_type.xml',
        'import/import_libraties.xml',
        'views/pos_config.xml',
        'views/pos_config_image.xml',
        'views/pos_session.xml',
        'views/product_template.xml',
        'views/pos_order.xml',
        'views/sale_order.xml',
        'views/pos_loyalty.xml',
        'views/res_partner_credit.xml',
        'views/res_partner_group.xml',
        'views/res_partner_type.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/pos_promotion.xml',
        'views/account_journal.xml',
        'views/pos_voucher.xml',
        'views/pos_branch.xml',
        'views/pos_tag.xml',
        'views/pos_note.xml',
        'views/pos_combo_item.xml',
        'views/product_variant.xml',
        'views/product_barcode.xml',
        'views/product_pricelist.xml',
        'views/stock_production_lot.xml',
        'views/pos_quickly_payment.xml',
        'views/pos_global_discount.xml',
        'views/account_invoice.xml',
        'views/purchase_order.xml',
        'views/medical_insurance.xml',
        'views/pos_call_log.xml',
        'views/pos_category.xml',
        'views/pos_cache_database.xml',
        'views/sale_extra.xml',
        'views/product_packaging.xml',
        'views/stock_location.xml',
        'views/pos_iot.xml',
        'views/res_currency.xml',
        'views/pos_sync_session_log.xml',
        'wizards/sale_order_line_insert.xml',
        'wizards/remove_pos_order.xml',
        'wizards/pos_remote_session.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    "currency": 'EUR',
    'installable': True,
    'application': True,
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com',
    "license": "OPL-1",
    'post_init_hook': '_auto_clean_cache_when_installed',
}