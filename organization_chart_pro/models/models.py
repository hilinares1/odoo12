# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OrgChartDepartment(models.Model):
	_name = 'org.chart.department'

	name = fields.Char("Org Chart Department")

	@api.model
	def get_department_data(self):
		data = {
			'id': -1,
			'name': self.env.user.company_id.name,
			'title': '',
			'children': [],
		}
		departments = self.env['hr.department'].search([('parent_id','=',False)])
		for department in departments:
			data['children'].append(self.get_children(department, 'middle-level'))

		return {'values': data}


	@api.model
	def get_children(self, dep, style=False):
		data = []
		dep_data = {'id':dep.id ,'name': dep.name, 'title': dep.manager_id.name}
		childrens = self.env['hr.department'].search([('parent_id','=',dep.id)])
		for child in childrens:
			sub_child = self.env['hr.department'].search([('parent_id','=',child.id)])
			next_style= self._get_style(style)
			if not sub_child:
				data.append({'id':child.id ,'name': child.name, 'title': child.manager_id.name, 'className': next_style})
			else:
				data.append(self.get_children(child, next_style))

		if childrens:
			dep_data['children'] = data
		if style:
			dep_data['className'] = style

		return dep_data


	def _get_style(self, last_style):
		if last_style == 'middle-level':
			return 'product-dept'
		if last_style == 'product-dept':
			return 'rd-dept'
		if last_style == 'rd-dept':
			return 'pipeline1'
		if last_style == 'pipeline1':
			return 'frontend1'

		return 'middle-level'

	# Get Dep Form ID
	@api.model
	def get_dep_form_id(self):
		return {'form_id': self.env.ref('organization_chart_pro.chart_department_form').id}


class HrDepartment(models.TransientModel):
	_name="slife.department"

	@api.model
	def default_dep_id(self):
		if self.env.context.get('dep_id') and int(self.env.context.get('dep_id')) > 0:
			return int(self.env.context.get('dep_id'))
		return False

	@api.model
	def default_parent_id(self):
		if self.env.context.get('parent_id') and int(self.env.context.get('parent_id')) > 0:
			return int(self.env.context.get('parent_id'))
		if self.env.context.get('dep_id') and int(self.env.context.get('dep_id')) > 0:
			dep_id = self.env['hr.department'].browse(int(self.env.context.get('dep_id')))
			return dep_id.parent_id.id
		return False

	@api.model
	def default_name(self):
		if self.env.context.get('dep_id') and int(self.env.context.get('dep_id')) > 0:
			dep_id = self.env['hr.department'].browse(int(self.env.context.get('dep_id')))
			return dep_id.name
		return False

	@api.model
	def default_manager_id(self):
		if self.env.context.get('dep_id') and int(self.env.context.get('dep_id')) > 0:
			dep_id = self.env['hr.department'].browse(int(self.env.context.get('dep_id')))
			return dep_id.manager_id.id
		return False

	department_id = fields.Many2one('hr.department', string='Department ID', default=default_dep_id)
	parent_id = fields.Many2one('hr.department', string='Parent Department', index=True, default=default_parent_id)
	name = fields.Char('Department Name', required=True, default=default_name)
	manager_id = fields.Many2one('hr.employee', string='Manager', track_visibility='onchange', default=default_manager_id)

	@api.multi
	def action_to_add_noeud(self):
		for record in self:
			self.env['hr.department'].create({
				'name': record.name,
				'parent_id': record.parent_id.id,
				'manager_id': record.manager_id.id,
			})
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}

	@api.multi
	def action_to_edit_noeud(self):
		for record in self:
			if record.department_id:
				record.department_id.write({
					'name': record.name,
					'parent_id': record.parent_id.id,
					'manager_id': record.manager_id.id,
				})
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}
