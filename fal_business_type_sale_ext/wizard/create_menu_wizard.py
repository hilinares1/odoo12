from odoo import api, fields, models, _
from odoo.exceptions import Warning
import ast
import logging

_logger = logging.getLogger(__name__)


class CreateMenuWizard(models.TransientModel):
    _inherit = "create.menu.wizard"


    select_action = fields.Selection(selection_add=[('sale', 'Sale')])

    @api.multi
    def create_business_menu(self):
        super(CreateMenuWizard, self).create_business_menu()
        if self.select_action == 'sale':
            self.create_menu_for_sale()

    @api.multi
    def create_menu_for_sale(self):
        menu_env = self.env['ir.ui.menu']
        action_base = self.env.ref('sale.action_quotations_with_onboarding');
        action_created = action_base.copy()
        try:
            replace_text = action_created.context
            replace_text = replace_text.replace(" ","")
            context_dict = ast.literal_eval(replace_text)
            context_dict.update({'default_fal_business_type':self._context.get('active_id')})
        except:
            context_dict = {'default_fal_business_type':self._context.get('active_id')}
        
        action_created.write({
            'name': 'Quotations',
            'domain':[('fal_business_type', '=', self._context.get('active_id'))],
            'context': str(context_dict)
            })

        menu_env.create({
                'name': self.name,
                'parent_id': self.parent_menu_id.id,
                'action':''.join(['ir.actions.act_window',',',str(action_created.id)])})
