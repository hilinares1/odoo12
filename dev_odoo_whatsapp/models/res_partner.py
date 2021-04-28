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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    class ResPartner(models.Model):
        _inherit = 'res.partner'

    @api.multi
    def check_number_validity(self):
        if not self.mobile.isdigit():
            raise ValidationError(_('''Please remove letters from the mobile number'''))

    @api.multi
    def send_whatsapp_message_data(self):
        if not self.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.name))
        else:
            self.check_number_validity()
        if self.country_id and self.country_id.phone_code:
            url = 'https://api.whatsapp.com/send?phone='
            url += str(self.country_id.phone_code) + str(self.mobile)
            return {'type': 'ir.actions.act_url', 'name': "Sending Message", 'target': 'new', 'url': url}
        else:
            if not self.country_id:
                raise ValidationError(_('''Please select Country for : %s''') % (self.name))
            if self.country_id:
                if not self.country_id.phone_code:
                    raise ValidationError(_('''Please specify Country Calling Code for : %s''') % (self.country_id.name))

    @api.multi
    def send_due_whatsapp_message_data(self):
        if not self.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.name))
        else:
            self.check_number_validity()
        if self.country_id and self.country_id.phone_code:
            url = 'https://web.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.name.replace(' ', '*%20*') + ',*%0a'
            currency = self.currency_id.symbol
            message += '%0aYour%20reaming%20due%20balance%20is%20*' + str(self.credit) + '*%20*' + currency + '*%20please%20pay%20immediately%0a%0a'
            if self.company_id:
                message += '*From*%20*:*%20*' + self.company_id.name + '*'
            url += str(self.country_id.phone_code) + str(self.mobile) + "&text=" + message
            return {'type': 'ir.actions.act_url', 'name': "Sending Message", 'target': 'new', 'url': url}
        else:
            if not self.country_id:
                raise ValidationError(_('''Please select Country for : %s''') % (self.name))
            if self.country_id:
                if not self.country_id.phone_code:
                    raise ValidationError(_('''Please specify Country Calling Code for : %s''') % (self.country_id.name))

    @api.multi
    def send_due_whatsapp_message_from_mobile(self):
        if not self.mobile:
            raise ValidationError(_('''Please specify mobile number for : %s''') % (self.name))
        else:
            self.check_number_validity()
        if self.country_id and self.country_id.phone_code:
            url = 'https://api.whatsapp.com/send?phone='
            message = 'Hello%20*' + self.name.replace(' ', '*%20*') + ',*%0a'
            currency = self.currency_id.symbol
            message += '%0aYour%20reaming%20due%20balance%20is%20*' + str(self.credit) + '*%20*' + currency + '*%20please%20pay%20immediately%0a%0a'
            if self.company_id:
                message += '*From*%20*:*%20*' + self.company_id.name + '*'
            url += str(self.country_id.phone_code) + str(self.mobile) + '&text=' + message
            return {'type': 'ir.actions.act_url', 'name': "Sending Message", 'target': 'new', 'url': url}
        else:
            if not self.country_id:
                raise ValidationError(_('''Please select Country for : %s''') % (self.name))
            if self.country_id:
                if not self.country_id.phone_code:
                    raise ValidationError(_('''Please specify Country Calling Code for : %s''') % (self.country_id.name))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
