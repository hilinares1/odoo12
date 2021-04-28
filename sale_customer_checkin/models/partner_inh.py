# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from math import sin, cos, sqrt, atan2, radians
from odoo.fields import Date, Datetime
import datetime,re
class geloc_hr_employee(models.Model):
    _inherit = 'res.partner'

    customer_visits_ids = fields.One2many(comodel_name="tt.customers.visits", inverse_name="partner_id", string="Customer Visits", required=False, )
    @api.model
    def location_checkin(self,userid=False,partnerid=False,lat=False,lon=False):
        create_checkin = {}
        create_checkin['visit_date'] =Datetime.now()
        create_checkin['user_id'] =userid
        create_checkin['partner_id'] =partnerid
        partner = self.env['res.partner'].search([('id','=',partnerid)])
        R = 6373.0 * 1000
        lat1 = radians(abs(lat))
        lon1 = radians(abs(lon))
        lat2 = radians(abs(partner.partner_latitude))
        lon2 = radians(abs(partner.partner_longitude))
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        create_checkin['distance'] = round(distance,2)
        self.customer_visits_ids.create(create_checkin)

        return True
    def location_checkin_dummy(self):
        return True

