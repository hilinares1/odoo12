# -*- coding: utf-8 -*-
{
    "name": "CRM Duplicates Real Time Search",
    "version": "12.0.1.0.3",
    "category": "Sales",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/crm-duplicates-real-time-search-254",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "crm"
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/crm_lead_view.xml",
        "views/res_partner_view.xml",
        "data/data.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool for real-time control of customers' and opportunities duplicates",
    "description": """
    This is the sales managers' tool to exclude double work and broken communication through fore-handed exposure of duplicates of leads, opportunities and customers.

    If you do not use CRM and searches for the tool only for partners' duplicates, look at the tool <a href='https://apps.odoo.com/apps/modules/12.0/partner_duplicates/'>Contacts Duplicates Real Time Search</a>
    Search of duplicates is <strong>real-time</strong>. You see results as soon as you save a partner or an opportunity
    The tool is fully <strong>configurable</strong>. Duplicates are defined according to your flexibly set up rules
    Use <i>rigid</i> criteria to fully <strong>exclude duplicates creation</strong>. Odoo would not allow salespersons to save a customer or an opportunity, if any duplicates were found by rigid rules
    Use <i>soft</i> criteria to warn salespersons of <strong>possible</strong> duplicates but not restrict them in such duplicates creation. An instance access to potential duplicates is available from form and kanban views. Besides, use the special filter for duplicates analysis
    As duplicates criteria use any field of the following types: char (name, email, phone, mobile, etc.), text (descriptions), many2one (reference for a parent company or a related customer), selection (for instance, type), date and datetime (e.g. birthday), integer and float (any unique code or even planned revenue)
    A document is considered as a duplicate, if it satisfies <strong>any</strong> of criteria. For all types except 'char', a duplicate should have absolutely the same value (e.g. '123' = '123', but '123' is not equal '1234'). 
    <i>[Only for soft search]</i> For char fields it is the operator 'ilike', thus, 'agro' is considered to be a potential duplicate of 'Agrolait' (but Agrolait is not considered as a duplicate of 'agro')
    The module supports <strong>multi companies</strong>. Duplicates are searched within a certain company. Thus, there may be equal objects related to different corporates
    The app is fully compatible with the Odoo standard tool to merge opportunities
    Configure soft and rigid criteria to search duplicates of customers and opportunities
    Users can't save a customer if there is a rigid duplicate found
    Warn salespersons of possible customers duplicates
    Instant access to customer possible duplicates from kanban
    Partners overall duplicates analysis
    Partners tree: observe potential duplciates counter
    Salespersons are forbidden save an opportunity if there is a rigid duplicate found
    Warn salespersons of possible opportunites duplicates
    One-click access for opportunities duplicates from kanban view
    Filter opportunities with possible duplicates
    Number of potential opportunities duplicates right in the opportunities' list
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "86.0",
    "currency": "EUR",
}