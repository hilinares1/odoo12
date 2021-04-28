# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Odoo Integration',
    'version': '12.0.1.0.4',
    'category': 'Tools',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'http://www.prixgen.com.com',
    'license': 'OPL-1',
    'summary': 'WhatsApp Integration with Odoo',
    'description': """
This module can be used to send messages to WhatsApp
----------------------------------------------------
Send Messages via WhatsApp
Core module for WhatsApp Odoo Integration
""",
    'depends': ['base', 'base_setup'],
    'data': [
        'wizard/send_wp_msg_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/mobile_widget.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price': 150,

}
