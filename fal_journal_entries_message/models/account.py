from odoo import models, fields, api, _


class account_move(models.Model):
    _name = "account.move"
    _inherit = [
        'account.move', 'mail.thread',
        'mail.activity.mixin', 'portal.mixin']

    state = fields.Selection(track_visibility='onchange')
    date = fields.Date(track_visibility='onchange')
    ref = fields.Char(track_visibility='onchange')
    # journal_id = fields.Many2one(track_visibility='onchange')

    @api.multi
    def write(self, values):
        for move in self:
            message = _("""
                <p>Old Move Line : </p>
                <ul>
                """)
            for old_move_line in move.line_ids:
                message += "<li>"
                message += old_move_line.account_id.display_name or "/"
                message += _(" [ ")
                message += old_move_line.partner_id and old_move_line.partner_id.display_name or "/"
                message += _(", ")
                message += old_move_line.name or "/"
                message += _(" ] - D: ")
                message += str(old_move_line.debit)
                message += _(" C: ")
                message += str(old_move_line.credit)
                message += "</li>"
            message += "</ul>"
            message_id = move.message_post(
                subject=_("Journal Entries Changed"),
                body=message,
            )

            if not isinstance(message_id, int):
                message_id = message_id.id
            self.env['mail.message'].browse(message_id).update(
                {'model': 'account.move', 'res_id': move.id})
            values['message_ids'] = [(4, message_id)]
        res = super(account_move, self).write(values)
        return res
