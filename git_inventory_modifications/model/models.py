from odoo import models, fields


class resPartnerInherit(models.Model):
    # _name = 'res.partner'
    _inherit = 'stock.inventory'

    # date = fields.Datetime(
    #     'Inventory Date',
    #     readonly=False, required=True,
    #     default=fields.Datetime.now,
    #     help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
    #          "If the inventory adjustment is validated, date at which the inventory adjustment has been validated.")

    date = fields.Datetime(readonly=False)





