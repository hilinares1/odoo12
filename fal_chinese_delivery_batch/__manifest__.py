{
    "name": "Chinese Delivery Batch",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Inventory',
    'summary': 'Module to add China delivery batches.',
    'website': 'https://falinwa.com',
    "description": """
        Module to add delivery batches with fapiao vat.
    """,
    "depends": [
        'fal_delivery_batch',
        'fal_invoice_delivery_fee'
    ],
    'data': [
        'views/fal_delivery_batch_view.xml',
        'report/exportation_contract_report.xml',
        'report/exportation_invoice_report.xml',
        'report/exportation_packing_list_for_customs_report.xml',
        'report/exportation_packing_list_for_customer_report.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
