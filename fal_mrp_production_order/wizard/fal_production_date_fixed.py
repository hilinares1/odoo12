from odoo import fields, models, api


class fal_fill_production_date_fixed(models.TransientModel):
    _name = "fal.fill.production.date.fixed"
    _description = "Fill Production Date Fix Wizard"

    @api.multi
    def button_assign_production_date_fixed(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        source = self.env['fal.production.order'].browse(active_ids)
        source.production_fixed()
