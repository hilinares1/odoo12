# -*- coding: utf-8 -*-

{
    'name': 'Theme Stoneware',
    'category': 'Theme/Ecommerce',
    'summary': 'Theme Stoneware is a Odoo theme with advanced ecommerce feature, extremely customizable and fully responsive',
    'version': '1.10',
    'author': 'Atharva System',
    'sequence': 1000,
	'license' : 'OPL-1',
    'support': 'support@atharvasystem.com',
    'website' : 'http://www.atharvasystem.com',
    'description': """
Theme Stoneware is  is a Odoo theme with advanced ecommerce feature, extremely customizable and fully responsive. It's suitable for any e-commerce sites.
Start your Odoo store right away with The Alan theme.
Corporate theme,
Creative theme,
Ecommerce theme,
Education theme,
Entertainment theme,
Personal theme,
Services theme,
Technology theme,
Business theme,
Multipurpose odoo theme,
Multi-purpose theme,
        """,
    'depends': ['website_theme_install'],
    'data': [
        'views/customize_template.xml',
        'views/templates.xml',
        'data/theme_stoneware_data.xml',  
    ],
    'live_test_url': 'http://theme-stoneware-v12.atharvasystem.com/',
	'images': ['static/description/stoneware_desc.png',
		'static/description/stoneware_screenshot.png'
	],
    'price': 199.00,
    'currency': 'EUR',
    'application': False,
}
