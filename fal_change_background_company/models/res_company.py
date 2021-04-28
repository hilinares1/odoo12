from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    background_image = fields.Binary(string="Home Menu Background Image", attachment=True)
    background_image_fname = fields.Char(string="Home Menu Background Image Name")
