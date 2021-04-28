
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Sale Order Status",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "category": "Sales",
    "summary": "This module useful to get status of delivery and invoices of sale orders. Easily filters sale orders with delivered, partial delivered, paid, partially paid.",
    "description": """
    
    This module useful to get status of delivery and invoices of sale orders. Easily filters sale orders with delivered, partial delivered, paid, partially paid.     

                    """,    
    "version":"11.0.1",
    "depends" : ["base","sale","sale_management","stock","account"],
    "application" : True,
    "data" : ['views/sale_view.xml',
            ],            
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 13,
    "currency": "EUR"   
}
