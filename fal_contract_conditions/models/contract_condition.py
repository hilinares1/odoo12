from odoo import models, fields


class contract_condition_falinwa(models.Model):
    _name = "contract.condition"
    _description = "Contract Condition"

    name = fields.Char(string='Name', size=64, required=True)
    content = fields.Text(string='Content', required=True)
