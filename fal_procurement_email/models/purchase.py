# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from datetime import datetime

PARTNER_KEYS = ['partner_id', 'partner', 'contact', 'vendor', 'supplier']
PRODUCT_KEYS = ['product', 'product_id', 'fal_req_product_id']
DESCRIPTION_KEYS = ['description', 'desc', 'fal_req_product_description']
COMMENT_KEYS = ['comment', 'comments', 'fal_warehouse_manager_comment']
QTY_KEYS = ['quantity', 'qty', 'fal_req_product_qty']


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        # look for matching alias
        # check if match with procurement alias

        email_from_full = msg_dict.get('email_from', "")
        email_from_list = email_from_full.split('<')
        email_from = False
        for item in email_from_list:
            if '>' in item:
                email_from = item.replace('>', '')

        email_to = msg_dict.get('to', False)

        email_to_localpart = (tools.email_split(email_to) or [''])[0].split('@', 1)[0].lower()
        
        dest_aliases = self.env['mail.alias'].search([
            '&', 
            ('alias_name', '!=', False),
            ('alias_name', '=', email_to_localpart)
            ], limit=1)

        procurement_alias = self.env.ref('fal_procurement_email.mail_alias_procurement') or False

        if procurement_alias and procurement_alias == dest_aliases:
            UserSudo = self.env['res.users'].sudo()
            if not custom_values:
                custom_values = {}
            custom_values['state'] = 'procurement_request'
            custom_values['name'] = 'New'
            custom_values['date_order'] = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if email_from:
                email_address = tools.email_escape_char(email_from)
                # search user with this email address
                users = UserSudo.search([
                    ('email', '=ilike', email_address)
                    ], limit=1)
                if not users:
                    # second try
                    email_brackets = "<%s>" % email_address
                    users = UserSudo.search([
                        ('email', 'ilike', email_brackets)
                        ], limit=1)
                if users:
                    custom_values['fal_req_user_id'] = users.id
                    if users.company_id:
                        custom_values['company_id'] = users.company_id.id
                    if users.company_id and users.company_id.currency_id:
                        custom_values['currency_id'] = users.company_id.currency_id.id

                body = msg_dict.get('body', "")

                body_dict = self._parse_procurement_body(body)
                if body_dict.get('partner_id'):
                    custom_values['partner_id'] = body_dict['partner_id']

                if body_dict.get('fal_req_product_id'):
                    custom_values['fal_req_product_id'] = body_dict['fal_req_product_id']

                if body_dict.get('fal_req_uom_id'):
                    custom_values['fal_req_uom_id'] = body_dict['fal_req_uom_id']

                if body_dict.get('fal_req_product_description'):
                    custom_values['fal_req_product_description'] = body_dict['fal_req_product_description']

                if body_dict.get('fal_warehouse_manager_comment'):
                    custom_values['fal_warehouse_manager_comment'] = body_dict['fal_warehouse_manager_comment']

                if body_dict.get('fal_req_product_qty'):
                    custom_values['fal_req_product_qty'] = body_dict['fal_req_product_qty']

                if not custom_values.get('company_id', False):
                    custom_values['company_id'] = self.env.user.company_id.id
                if not custom_values.get('currency_id', False):
                    custom_values['currency_id'] = self.env.user.company_id.currency_id.id

        return super(PurchaseOrder, self).message_new(msg_dict, custom_values)

    @api.model
    def _parse_procurement_body(self, body):
        res = {}
        body_split = body.split('[')
        key_value = []
        for item in body_split:
            item_val = item.split(']')
            if item_val and item_val[0]:
                key_value.append(item_val[0])

        for item in key_value:
            # check if item has allowed separator (':')
            key_val = item.split(':')

            if not key_val or len(key_val) < 2:
                continue

            key = key_val[0].lower()
            val = key_val[1].strip()
            key = key.strip()

            # strip single quote
            key = key.strip("\'")
            val = val.strip("\'")

            # strip double quote
            key = key.strip("\"")
            val = val.strip("\"")

            if key in PARTNER_KEYS:
                partner = self._parse_procurement_partner(val)
                if partner:
                    res['partner_id'] = partner.id

            if key in PRODUCT_KEYS:
                product = self._parse_procurement_product(val)
                if product:
                    res['fal_req_product_id'] = product.id
                    res['fal_req_uom_id'] = product.uom_id.id or False

            if key in DESCRIPTION_KEYS:
                res['fal_req_product_description'] = str(val)

            if key in COMMENT_KEYS:
                res['fal_warehouse_manager_comment'] = str(val)

            if key in QTY_KEYS:
                try:
                    res['fal_req_product_qty'] = int(val)
                except:
                    pass
        return res

    @api.model
    def _parse_procurement_partner(self, val):
        PartnerSudo = self.env['res.partner'].sudo()
        partner = False

        try:
            # try to treat val as integer
            partner_id = int(val)
            partner = PartnerSudo.browse(partner_id)
        except Exception as e:
            # val is string
            partner = PartnerSudo.search([
                ('name', 'ilike', val)
                ], limit=1)

        # if not found, and val has @
        # try to search on email
        if '@' in val:
            partner = PartnerSudo.search([
                    ('email', '=ilike', val)
                    ], limit=1)

        # last try
        # get first word, search on name
        if not partner:
            val_list = val.split(' ')
            if val_list and val_list[0]:
                val = val_list[0]
                partner = PartnerSudo.search([
                    ('name', 'ilike', val)
                    ], limit=1)

        return partner


    @api.model
    def _parse_procurement_product(self, val):
        ProductSudo = self.env['product.product'].sudo()
        product = False

        try:
            # try to treat val as integer
            product_id = int(val)
            product = ProductSudo.browse(product_id)
        except Exception as e:
            # val is string
            product = ProductSudo.search([
                ('name', 'ilike', val)
                ], limit=1)

        # if not found, search in internal reference (default_code)
        if not product:
            product = ProductSudo.search([
                ('default_code', 'ilike', val)
                ], limit=1)

        # last try
        # get first word, search on name
        if not product:
            val_list = val.split(' ')
            if val_list and val_list[0]:
                val = val_list[0]
                product = ProductSudo.search([
                    ('name', 'ilike', val)
                    ], limit=1)

        return product
