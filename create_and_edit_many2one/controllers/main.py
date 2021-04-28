from odoo import http
from odoo.http import request


class create_and_edit_many2one(http.Controller):

    @http.route(
        '/web/create_and_edit_many2one/create_edit_allowed',
        type='json',
        auth='user'
    )
    def create_edit_allowed(self, req):
        Model_data_obj = request.env['ir.model.data']
        group_id = Model_data_obj.xmlid_to_object(
            'create_and_edit_many2one.group_allo_create_edit_many2one').id
        if group_id in req.env.user.groups_id.ids:
            return True
        return False
