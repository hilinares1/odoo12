# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import main

import logging
_logger = logging.getLogger(__name__)

class OrgChart(http.Controller):

	@http.route('/orgchart/update', methods=['POST'], csrf=False)
	def update_org_chart(self, child, last_parent, new_parent):
		if new_parent:
			dep = request.env['hr.department'].search([('id','=',child)])
			parent = request.env['hr.department'].search([('id','=',new_parent)])
			dep.write({'parent_id': parent.id})

		return ""
