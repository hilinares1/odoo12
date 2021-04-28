# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class fal_account_invoice_line_add_aci_wizard(models.TransientModel):
    """Event Confirmation"""
    _name = "fal.account.invoice.line.add.aci.wizard"

    fal_customer_account_invoice_id = fields.Many2one(
        "account.invoice",
        string="ACI",
        domain="[('type','=','out_invoice')]"
    )
    fal_customer_account_invoice_line_ids = fields.Many2many(
        "account.invoice.line",
        "wizard_supplier_aci_line_customer_aci_line_rel",
        "wizard_supplier_account_invoice_line_id",
        "customer_account_invoice_line_id",
        string="ACI Line",
        domain="[('invoice_id','=',fal_customer_account_invoice_id)]"
    )
    fal_no_match_reason = fields.Selection([
        ('non_business_cost', 'Non-Business Costs'),
        ('aci_end_of_fy', 'ACI end of FY'),
        ('sold_on_stock', 'Sold on Stock'),
    ], string="No Match Reason", readonly=False)
    fal_mathching_ok = fields.Boolean("Match", readonly=False)

    @api.multi
    def confirm(self):
        for wizard in self:
            self.env['account.invoice.line'].browse(self._context['active_id']).write({
                'fal_customer_account_invoice_id': wizard.fal_customer_account_invoice_id.id,
                'fal_customer_account_invoice_line_ids': [(6, 0, wizard.fal_customer_account_invoice_line_ids.ids)],
                'fal_mathching_ok': wizard.fal_mathching_ok,
                'fal_no_match_reason': wizard.fal_no_match_reason
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
