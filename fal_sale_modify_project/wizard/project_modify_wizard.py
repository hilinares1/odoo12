# -*- coding: utf-8 -*-
from odoo import fields, models, api


class project_modify_wizard(models.TransientModel):
    _name = "project.modify.wizard"
    _description = "Project Modify Wizard"

    project_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account'
    )

    @api.multi
    def update_project_id(self):
        context = dict(self._context)
        active_id = context.get('active_id', False)
        sale_order_obj = self.env['sale.order'].browse(active_id)

        sale_order_obj.write({
            'analytic_account_id': self.project_id.id
        })

        for invoice_id in sale_order_obj.invoice_ids:
            for invoice_line_id in invoice_id.invoice_line_ids:
                invoice_line_id.write({
                    'account_analytic_id': self.project_id.id
                })

            if invoice_id.move_id:
                for move_line_id in invoice_id.move_id.line_ids:
                    if move_line_id.credit:
                        move_line_id.write({
                            'analytic_account_id': self.project_id.id
                        })
