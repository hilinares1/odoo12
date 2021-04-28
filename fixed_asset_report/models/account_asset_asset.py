""" init object account.asset.asset """

import logging

from odoo import fields, models, api

LOGGER = logging.getLogger(__name__)


class AccountAssetAsset(models.Model):
    """ init object account.asset.asset """
    _inherit = 'account.asset.asset'

    asset_code = fields.Char(readonly=True)
    manufacturer = fields.Char()
    serial_number = fields.Char()
    model_number = fields.Char()

    @api.model
    def create(self, vals_list):
        """
        Override Create to add sequence.
        :param vals:
        """
        vals_list['asset_code'] = self.env['ir.sequence'].next_by_code(
            'account.asset.asset')
        res = super(AccountAssetAsset, self).create(vals_list)
        return res
