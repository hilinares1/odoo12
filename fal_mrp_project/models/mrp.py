from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account',
        help='The analytic account related to a Manufacturing Order.'
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(MrpProduction, self).onchange_product_id()
        if self.product_id:
            self.project_id = self.product_id.fal_project_id.id
        return res
