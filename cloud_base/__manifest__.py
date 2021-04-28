# -*- coding: utf-8 -*-
{
    "name": "Cloud Storage Solutions",
    "version": "12.0.1.3.6",
    "category": "Document Management",
    "author": "Odoo Tools",
    "website": "https://odootools.com/apps/12.0/cloud-storage-solutions-230",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "document",
        "base_setup"
    ],
    "data": [
        "data/data.xml",
        "data/cron.xml",
        "data/sync_formats_data.xml",
        "views/sync_model.xml",
        "views/ir_attachment.xml",
        "views/sync_log.xml",
        "views/res_config_settings.xml",
        "views/view.xml",
        "security/ir.model.access.csv"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The technical core to synchronize your Cloud storage solution with Odoo",
    "description": """
    Odoo document system is clear and comfortable to use. However, it is not designed to work with files as specific cloud storage solutions like OneDrive, GoogleDrive, OwnCloud, and DropBox do.  To process attachments users need to download a file, to change it, and to upload back.  Documents are not synced locally and Odoo doesn't have powerful previewers and editors. Specific cloud storage clients don't have such disadvantages. This tool is a <strong>technical core</strong> to provide logic of automatic and bilateral files synchronisation between Odoo and your cloud storage solution.

    This module is a technical core and is not of use without a real client app. Please select a desired one below
    <a href='https://apps.odoo.com/apps/modules/12.0/onedrive/'>OneDrive / SharePoint</a>
    <a href='https://apps.odoo.com/apps/modules/12.0/owncloud_odoo/'>OwnCLoud / NextCloud</a>
    <a href='https://apps.odoo.com/apps/modules/12.0/dropbox/'>DropBox</a>
    <a href='https://apps.odoo.com/apps/modules/12.0/google_drive_odoo/'>Google Drive</a>
""",
    "images": [
        "static/description/main.png"
    ],
    "price": "100.0",
    "currency": "EUR",
}