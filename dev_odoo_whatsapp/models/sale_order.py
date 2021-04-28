# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, api, _
from odoo.exceptions import ValidationError


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def send_whatsapp_message_data(self):
        if not self.partner_id.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.partner_id.name))
        else:
            self.partner_id.check_number_validity()
        if self.partner_id.country_id and self.partner_id.country_id.phone_code:
            url = 'https://web.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.partner_id.name.replace(' ', '*%20*') + ',*%0a'
            message += '%0aNo%20Pesanan%20Anda%20*' + self.name + '*%20is%20generated%20with%20bellow%20details%0a%0a'
            message1 = ''
            currency = self.pricelist_id.currency_id.symbol
            for line in self.order_line:
                name = line.name
                name = name.replace(' ', '%20')
                message1 += '*Produk*%20*:*%20' + name + '%0a'
                message1 += '*Quantity*%20*:*%20' + str(line.product_uom_qty) + '%0a'
                message1 += '*Harga*%20*:*%20' + str(line.price_subtotal) + '%20' + currency + '%0a'
                message1 += '_____________________%0a'

            message += message1
            message += '%0a*Total*%20*:*%20*' + str(self.amount_total) + '*%20*' + currency + '*%0a%0a'
            message += '%0aTerima%20Kasih%20Atas%20Kerjasama%20nya%20' + '%0a'
            message += '*From*%20*:*%20*' + self.company_id.name + '*'
            url += str(self.partner_id.country_id.phone_code) + str(self.partner_id.mobile) + '&text=' + message
            return {'type': 'ir.actions.act_url', 'name': "Sending Message", 'target': 'new', 'url': url}
        else:
            if not self.partner_id.country_id:
                raise ValidationError(_('''Please select Country for : %s''') % (self.partner_id.name))
            if self.partner_id.country_id:
                if not self.partner_id.country_id.phone_code:
                    raise ValidationError(_('''Please specify Country Calling Code for : %s''') % (self.partner_id.country_id.name))

    @api.multi
    def send_sale_whatsapp_message_from_mobile(self):
        if not self.partner_id.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.partner_id.name))
        else:
            self.partner_id.check_number_validity()
        if self.partner_id.country_id and self.partner_id.country_id.phone_code:
            url = 'https://api.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.partner_id.name.replace(' ', '*%20*') + ',*%0a'
            message += '%0aYour%20sale%20order%20*' + self.name + '*%20is%20generated%20with%20bellow%20details%0a%0a'
            message1 = ''
            currency = self.pricelist_id.currency_id.symbol
            for line in self.order_line:
                name = line.name
                name = name.replace(' ', '%20')
                message1 += '*Product*%20*:*%20' + name + '%0a'
                message1 += '*Quantity*%20*:*%20' + str(line.product_uom_qty) + '%0a'
                message1 += '*Price*%20*:*%20' + str(line.price_subtotal) + '%20' + currency + '%0a'
                message1 += '_____________________%0a'

            message += message1
            message += '%0a*Total*%20*:*%20*' + str(self.amount_total) + '*%20*' + currency + '*%0a%0a'
            message += '*From*%20*:*%20*' + self.company_id.name + '*'
            url += str(self.partner_id.country_id.phone_code) + str(self.partner_id.mobile) + '&text=' + message
            return {'type': 'ir.actions.act_url', 'name': "Sending Message", 'target': 'new', 'url': url}
        else:
            if not self.partner_id.country_id:
                raise ValidationError(_('''Please select Country for : %s''') % (self.partner_id.name))
            if self.partner_id.country_id:
                if not self.partner_id.country_id.phone_code:
                    raise ValidationError(_('''Please specify Country Calling Code for : %s''') % (self.partner_id.country_id.name))



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
