from odoo import fields, models, api, _


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    fal_sign_template = fields.Many2one('sign.template', string='Document Contract Template')
    sign_request_count = fields.Integer(string='Sign Request', compute='_sign_request_count', default=0)

    @api.multi
    def contract_sign_request(self):
        form = self.env.ref('sign.sign_send_request_view_form', False)

        context = dict(self._context or {})
        context.update({
            'contract_template_id': self.fal_sign_template.id,
        })

        return {
            'name': _('Contract'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sign.send.request',
            'view_id': form.id,
            'target': 'new',
            'context': context,
        }

    def _sign_request_count(self):
        sign_request_obj = self.env['sign.request']
        sign_request_ids = sign_request_obj.search([])

        count_result = 0
        for record in sign_request_ids:
            partner_id = record.request_item_ids.filtered(lambda r: r.partner_id == self.employee_id.user_id.partner_id)

            if partner_id:
                count_result += 1

        self.sign_request_count = count_result

    @api.multi
    def open_sign_request_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sign Contract of %s' % self.employee_id.name),
            'view_mode': 'kanban',
            'res_model': 'sign.request',
            # 'context': context
        }
