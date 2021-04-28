# -*- coding: utf-8 -*-
{
    'name': 'Minimum And Maximum Price Of Product',
    
    'author' : 'Softhealer Technologies',
    
    'website': 'https://www.softhealer.com',
        
    'version': '12.0.1',
    
    'category': 'Sales',
    
    'summary': 'This module useful to set minimum and maximum selling price for product.',
    
    'description': """This module useful to set minimum and maximum selling price for product. Sales person can easily see minimum and maximum sale price so that will useful to make clear action in sales procedure without waiting for senior person.""",
    
    'depends': ['sale_management'],
    
    'data': [
        'views/sale_order_min_max_price.xml',
        'data/sale_order_price_group.xml',
        ],
    
    'images': ['static/description/background.png',],              
    
    'auto_install':False,
    'installable':True,
    'application':True,    

    "price": 15,
    "currency": "EUR"        
}
