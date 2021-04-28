from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    fal_project_share = fields.Boolean(string='Share project to all companies',
        help="Share your project to all companies defined in your instance.\n"
             " * Checked : project are visible for every companies, even if a company is defined on the project.\n"
             " * Unchecked : Each company can see only its project (project where company is defined). project not related to a company are visible for all companies.")

    fal_project_task_share = fields.Boolean(string='Share project task to all companies',
        help="Share your project task to all companies defined in your instance.\n"
             " * Checked : project task are visible for every companies, even if a company is defined on the project task.\n"
             " * Unchecked : Each company can see only its project task (project task where company is defined). project task not related to a company are visible for all companies.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            fal_project_share=not self.env.ref(
                'project.project_comp_rule').active,
            fal_project_task_share=not self.env.ref(
                'project.task_comp_rule').active,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.ref('project.project_comp_rule').write({
            'active': not self.fal_project_share})
        self.env.ref('project.task_comp_rule').write({
            'active': not self.fal_project_task_share})

