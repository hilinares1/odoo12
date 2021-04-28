{
    "name": "Invoice Delivery Fee",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Sale, Purchase & Invoicing',
    'summary': 'Module to add delivery fees on invoice.',
    'website': 'https://falinwa.com',
    "description": """
        Module to add delivery fees on invoice.
        Warning: This module can wok only if the VAT rate is the same for all the products.
        If no, the computed tax amount will not correspond to the fapiao tax amount.
    """,
    "depends": [
        'fal_invoice_additional_info',
        'fal_purchase_additional_info',
        'fal_sale_additional_info',
    ],
    'data': [
        'security/security.xml',
        'report/fal_report_saleorder_idf.xml',
        'report/fal_report_invoice_idf.xml',
        'report/fal_report_purchaseorder_idf.xml',
        'report/fal_report.xml',
        'views/account_invoice_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
