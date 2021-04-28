{
    "name": "Purchase Sequence",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Purchase',
    'summary': 'Add Purchase Sequence',
    'website': 'https://falinwa.com',
    "description": """
        Customize for sequence, not only request sequence for Supplier Order number, \
        but also  request sequence for Supplier quotation order number, and after \
        confirm quotation order, field of source document will show the quotation  number.
    """,
    "depends": [
        'purchase',
        'inter_company_rules'
    ],
    'data': [
        'views/order_sequence.xml',
        'views/purchase_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
