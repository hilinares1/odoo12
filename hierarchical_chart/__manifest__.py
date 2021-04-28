# -*- coding: utf-8 -*-
{
    'name': "hierarchical chart",

    'version': '1.0',
    'license': 'LGPL-3',

    'summary': """
        add hierarchical chart to odoo
    """,



    'description': """
        add the feature of leveled view to odoo
        
        after install this module make action in the xml like:
        * for account.analytic.account:
        <record id="hr_action_hierarchical_chart" model="ir.actions.client">
            <field name="name">Hierarchical Chart Of Analytic Account</field>
            <field name="tag">hierarchical_view</field>
            <field name="context">{'model': 'account.analytic.account'}</field>
        </record>

        and in the python add a hierarchical_chart_details method to your model here it is account.analytic.account (and you have to specify the parent_id)

        @api.model
        def hierarchical_chart_details(self):
            accounts = self.sudo().search([])
            accounts = accounts.read([])

            return ['code', 'name', 'partner_id', 'debit',
                    'credit', 'balance'], accounts
                    


    """,

    'author': "Alfadil",

    'support': 'alfadil.tabar@gmail.com',

    'category': 'tools',
    'images': ['static/description/icon.png'],

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'qweb': ["static/src/xml/hierarchical_chart_templates.xml"],


}
