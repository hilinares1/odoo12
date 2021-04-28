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


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def send_whatsapp_message_data(self):
        if not self.partner_id.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.partner_id.name))
        else:
            self.partner_id.check_number_validity()
        if self.partner_id.country_id and self.partner_id.country_id.phone_code:
            url = 'https://web.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.partner_id.name.replace(' ', '*%20*') + ',*%0a'
            number = 'Draft%20Invoice'
            if self.number:
                number = self.number
            message += '%0aYour%20Invoice%20*' + number + '*%20is%20generated%20with%20bellow%20details%0a%0a'
            message1 = ''
            currency = self.currency_id.symbol
            for line in self.invoice_line_ids:
                name = line.product_id.name
                name = name.replace(' ', '%20')
                message1 += '*Product*%20*:*%20' + name + '%0a'
                message1 += '*Quantity*%20*:*%20' + str(line.quantity) + '%0a'
                message1 += '*Price*%20*:*%20' + str(line.price_total) + '%20' + currency + '%0a'
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

    @api.multi
    def send_invoice_whatsapp_message_from_mobile(self):
        if not self.partner_id.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.partner_id.name))
        else:
            self.partner_id.check_number_validity()
        if self.partner_id.country_id and self.partner_id.country_id.phone_code:
            url = 'https://api.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.partner_id.name.replace(' ', '*%20*') + ',*%0a'
            number = 'Draft%20Invoice'
            if self.number:
                number = self.number
            message += '%0aYour%20Invoice%20*' + number + '*%20is%20generated%20with%20bellow%20details%0a%0a'
            message1 = ''
            currency = self.currency_id.symbol
            for line in self.invoice_line_ids:
                name = line.product_id.name
                name = name.replace(' ', '%20')
                message1 += '*Product*%20*:*%20' + name + '%0a'
                message1 += '*Quantity*%20*:*%20' + str(line.quantity) + '%0a'
                message1 += '*Price*%20*:*%20' + str(line.price_total) + '%20' + currency + '%0a'
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