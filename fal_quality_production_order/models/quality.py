from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    fal_production_order_id = fields.Many2one(
        'fal.production.order',
        string='Production Order',
        copy=False)


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    fal_production_order_id = fields.Many2one(
        'fal.production.order',
        string='Production Order',
        copy=False)

    def _values_alert(self):
        res = super(QualityCheck, self)._values_alert()
        res['fal_production_order_id'] = self.fal_production_order_id.id
        return res
