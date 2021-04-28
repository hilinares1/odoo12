{
    "name": "Delivery Batch",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Inventory',
    'summary': 'Module to add delivery batches.',
    'website': 'https://falinwa.com',
    "description": """
        Module to add delivery batches.
    """,
    "depends": [
        'stock_account',
        'fal_product_size_detail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_batch_data.xml',
        'wizard/fal_put_to_box.xml',
        'wizard/fal_register_delivery_batch.xml',
        'views/fal_delivery_batch_view.xml',
        'views/product_view.xml',
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
