# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions,_
from datetime import date, datetime, time, timedelta
import datetime,re
from odoo.fields import Date, Datetime
class CustomerVisits(models.Model):
    _name = 'tt.customers.visits'

    name = fields.Char(default=_("New"))
    visit_date = fields.Datetime(string="Visit Date", required=False, )
    user_id = fields.Many2one(comodel_name="res.users", string="User", required=False, )
    distance = fields.Float(string="Check In Distance", required=False)
    partner_id = fields.Many2one('res.partner',string="Partner")


