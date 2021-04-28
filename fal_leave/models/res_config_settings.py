# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fal_leave_remove_remaining_leave = fields.Boolean(
        string="Remove Remaining Leave")

    fal_leave_share = fields.Boolean(
        string="Share leave to all companies",
        help="Share your leave to all companies in your instance.\n"
             " * Checked : leaves are visible for every companies.\n"
             " * Unchecked : Each company can see only its leaves."
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            fal_leave_remove_remaining_leave=get_param(
                'fal_leave.remove_remaining_leave', 'False').lower() == 'true',
        )
        res.update(
            fal_leave_share=not self.env.ref(
                'hr_holidays.hr_leave_rule_multicompany').active,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('fal_leave.remove_remaining_leave', repr(
            self.fal_leave_remove_remaining_leave))

        if self.fal_leave_remove_remaining_leave:
            ircron = self.env.ref(
                'fal_leave.ir_cron_remove_remaining_leave_action')
            ircron.update({
                'active': True
            })
        else:
            ircron = self.env.ref(
                'fal_leave.ir_cron_remove_remaining_leave_action')
            ircron.update({
                'active': False
            })
        
        # remove employee multi-company rule
        self.env.ref('hr.hr_employee_comp_rule').write({
            'active': not self.fal_leave_share})
        
        # toggle active common leave feature
        self.env.ref('hr_holidays.hr_leave_rule_multicompany').write({
            'active': not self.fal_leave_share})
        
        self.env.ref('hr_holidays.hr_holidays_status_rule_multi_company').write({
            'active': not self.fal_leave_share})

        overview_menuitem = self.env.ref('hr_holidays.menu_hr_holidays_dashboard')
        groups_id = self.env.ref('hr_holidays.group_hr_holidays_manager').id
        if self.fal_leave_share:
            groups_id = self.env.ref('base.group_user').id

        overview_menuitem.write({
            'groups_id': [(6, 0, [groups_id])]
            })

    @api.model
    def _prepare_cron_leave_view_action(self, cronref):
        cron_id = self.env.ref(cronref)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.cron',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': cron_id.id,
        }

    @api.multi
    def open_cron_leave(self):
        if not self.fal_leave_remove_remaining_leave:
            return False
        return self._prepare_cron_leave_view_action(
            'fal_leave.ir_cron_remove_remaining_leave_action')
