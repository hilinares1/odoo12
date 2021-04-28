from odoo import fields, models, api
from odoo.exceptions import ValidationError


class FedState(models.Model):
    """ This will extend the res.country.state"""
    _inherit = 'res.country.state'

    region = fields.Char('Region', required=True)


class Contacts(models.Model):
    """This will extend res.partner"""
    _inherit = 'res.partner'

    region = fields.Char('Region', required=True, related='state_id.region')

    @api.onchange('region')
    def _check_region(self):
        """
        This will prevent the user for modifying the field

        :return: string. error!
        """
        for rec in self:
            if rec.region != rec.state_id.region:
                raise ValidationError('You are not allowed to change the Region!')

    # This will check the uniqueness of the field
    _sql_constraints = [
        ('vate_unique', 'unique(vat)', 'TIN already exist!!')
    ]
