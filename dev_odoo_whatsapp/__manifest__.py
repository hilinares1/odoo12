# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Odoo Send Whatsapp Message',
    'version': '12.0.1.1',
    'sequence': 1,
    'category': 'Sales Management',
    'description':
        """
 Odoo app send Whatsapp Message for Sale, Invoice, Payment and customer due balance
        
        odoo whatsapp
        odoo whatsapp send message 
        odoo whatsapp customer due balance 
        odoo whatsapp sale order message 
        odoo whatsapp invoice message 
        odoo whatsapp payment notification
Odoo Send Whatsapp Message
Send whatsapp message 
Manage Odoo Send Whatsapp Message
Manage send whatsapp message 
Odoo app send Whatsapp Message for Sale, Invoice, Payment and customer due balance
Easy to Send whatsapp message customer Due Balance.
Easy to Send whatsapp message in For Sale Order Product Details and Total
Easy to Send whatsapp message in For Purchase Order
Easy to Send whatsapp message in For Invoice Order
 Easy to Send whatsapp message in For Vendor Bill
Odoo Easy to Send whatsapp message customer Due Balance.
Odoo Easy to Send whatsapp message in For Sale Order Product Details and Total
Odoo Easy to Send whatsapp message in For Purchase Order
Odoo Easy to Send whatsapp message in For Invoice Order
Odoo Easy to Send whatsapp message in For Vendor Bill
Whatsapp web form 
Odoo whatsapp web form 
Manage whatsapp web form 
Odoo manage whatsapp web form 
Manage whatsapp message layout
Odoo Manage whatsapp message layout
    """,
    'summary': 'Odoo app send Whatsapp Message for Sale, Invoice, Payment and customer due balance',
    'depends': ['sale_management'],
    'data': [
        
        'views/account_invoice_views.xml',
        'views/sale_order_views.xml',
        'views/account_payment_view.xml',
        'views/res_partner_views.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':29.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
