# -*- coding: utf-8 -*-
from odoo import models, fields


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    fal_week_minimal_hour = fields.Float(
        string='Weekly Timesheet Minimal Workhours')
    fal_week_maximal_hour = fields.Float(
        string='Weekly Timesheet Maximal Workhours')
    fal_week_equal_hour = fields.Float(
        string='Weekly Timesheet Equal Workhours')
    fal_is_set_week_minimum_hour = fields.Boolean(
        string='Set Minimum Workhours')
    fal_is_set_week_equal_hour = fields.Boolean(
        string='Set Equal Workhours')
    fal_is_set_week_maximal_hour = fields.Boolean(
        string='Set Maximal Workhours')
