from odoo import models, api
from odoo.tools.translate import _


class res_users(models.Model):
    _name = "res.users"
    _inherit = ['res.users', 'mail.thread']

    @api.multi
    def write(self, values):
        for user in self:
            groups_class = self.env['res.groups']
            start_group = set(user.groups_id.ids)
            res = super(res_users, self).write(values)
            end_group = set(user.groups_id.ids)
            group_added = end_group - start_group
            group_removed = start_group - end_group

            if group_added or group_removed:
                message = _("""
                    <p>Access Right/Groups changed : </p>
                    <ul>
                    """)
                for difference in group_added:
                    message += "<li>"
                    message += groups_class.browse(difference).display_name
                    message += _(" : Added")
                    message += "</li>"
                for difference in group_removed:
                    message += "<li>"
                    message += groups_class.browse(difference).display_name
                    message += _(" : Removed")
                    message += "</li>"
                message += "</ul>"
                self.message_post(
                    subject=_("Access Right Changed"),
                    body=message,
                )
        res = super(res_users, self).write(values)
        return res

# end of res_users()
