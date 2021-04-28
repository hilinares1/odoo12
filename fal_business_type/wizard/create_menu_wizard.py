from odoo import api, fields, models, _


class CreateMenuWizard(models.TransientModel):
    _name = "create.menu.wizard"
    _description = 'Business unit create menu wizard'


    name = fields.Char(String='Menu', required=True)
    parent_menu_id = fields.Many2one('ir.ui.menu', String='Parent Menu')
    select_action = fields.Selection([], string='Menu Action', required=True)

    @api.multi
    def create_business_menu(self):
        pass        
