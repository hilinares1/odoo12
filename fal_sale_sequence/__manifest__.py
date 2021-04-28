{
    "name": "Sale Sequence",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Sale',
    'summary': 'Add Quotation sequence',
    'website': 'https://falinwa.com',
    "description": """
        Customize for sequence, not only request sequence for Customer Order number, \
        but also  request sequence for Customer quotation order number, and after \
        confirm quotation order, field of source document will show the quotation  number.
    """,
    "depends": [
        'sale',
        'inter_company_rules'
    ],
    'data': [
        'views/order_sequence.xml',
        'views/sale_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
