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
from datetime import datetime

class account_payment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def send_whatsapp_message_data(self):
        if not self.partner_id.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.partner_id.name))
        else:
            self.partner_id.check_number_validity()
        if self.partner_id.country_id and self.partner_id.country_id.phone_code:
            url = 'https://web.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.partner_id.name.replace(' ', '*%20*') + ',*%0a'
            currency = self.currency_id.symbol
            payment_name = ''
            if self.name:
                payment_name = self.name
            date = ''
            if self.payment_date:
                date = self.payment_date.strftime('%d-%m-%Y')
            message += '%0aPembayaran%20Senilai%20*' + currency + '*%20*' + str(self.amount) + '*%20telah%20kami%20terima%20pada%20Tanggal%20:%20*' + date + '*%20Utk%20Pembayaran%20Faktur%20:%20*' + payment_name + '*%0a%0a'
            message += '*Terima*%20*Kasih*%20*Atas*%20*Kerja*%20*Sama*%20*Nya*%20*'
            message += '*Apabila*%20*ada*%20*Perbedaan*%20*Nilai*%20*Pembayaran*%20,%20*Silakan*%20*Hubungi*%20*Kami*%20' + '%0a%0a'
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
    def send_payment_whatsapp_message_from_mobile(self):
        if not self.partner_id.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.partner_id.name))
        else:
            self.partner_id.check_number_validity()
        if self.partner_id.country_id and self.partner_id.country_id.phone_code:
            url = 'https://api.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.partner_id.name.replace(' ', '*%20*') + ',*%0a'
            currency = self.currency_id.symbol
            payment_name = ''
            if self.name:
                payment_name = self.name
            date = ''
            if self.payment_date:
                date = self.payment_date.strftime('%d-%m-%Y')
            message += '%0aPembayaran%20Senilai%20*' + currency + '*%20*' + str(self.amount) + '*%20telah%20kami%20terima%20pada%20Tanggal%20:%20*' + date + '*%20Utk%20Pembayaran%20Faktur%20:%20*' + payment_name + '*%0a%0a'
            message += '*Terima*%20*Kasih*%20*Atas*%20*Kerja*%20*Sama*%20*Nya*%20*'
            message += '*Apabila*%20*ada*%20*Perbedaan*%20*Nilai*%20*Pembayaran*%20,%20*Silakan*%20*Hubungi*%20*Kami*%20' + '%0a%0a'
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
