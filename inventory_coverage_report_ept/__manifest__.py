
{
    # App information
    'name': 'Inventory Coverage Report',
    'version': '12.0',
    'category': 'stock',
    'summary' : 'Inventory coverage report app for Odoo helps you to analyse your warehouse wise products stock availability, for next how many days your products will be there in stock.',
    'license': 'OPL-1',

    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Dependencies
    'depends': ['purchase', 'stock', 'sale'],

    # Views
    'data': [
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',

        'security/inventory_coverage_security.xml',
        'security/ir.model.access.csv',

        'views/base_menu_inventory_coverage.xml',
        'views/product_product_views.xml',
        'views/requisition_period_ept_views.xml',
        'views/product_template_views.xml',
        'views/requisition_fiscal_year_ept_views.xml',
        'views/forecast_sale_ept_views.xml',
        'views/forecast_sale_rule_ept_views.xml',
        'views/requisition_log_ept_views.xml',

        'wizardviews/inventory_coverage_report_res_setting_views.xml',
        'wizardviews/requisition_product_suggestion_ept_views.xml',
        'wizardviews/import_export_forecast_sale_ept_views.xml',
        'wizardviews/import_multi_products_sale_rule_ept_views.xml',
        'wizardviews/import_export_forecast_sale_rule_ept_views.xml',
        'wizardviews/calculate_average_daily_sale.xml',
        'wizardviews/mismatch_data_views.xml',
        'wizardviews/ads_report.xml',

        'report/forecast_sale_report_views.xml',
        'report/forecast_and_actual_sales_views.xml',
        'report/product_average_daily_sale_report.xml'
       
    ],

    # Odoo Store Specific       
    'images': ['static/description/Inventory-Coverage-Report-store-cover-image.jpg'],

    # Odoo Store Specific
    
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_load_extension',
    'live_test_url':'https://www.emiprotechnologies.com/free-trial?app=inventory-coverage-report-ept&version=12&edition=enterprise',
    'price': '149' ,
    'currency': 'EUR',


}
