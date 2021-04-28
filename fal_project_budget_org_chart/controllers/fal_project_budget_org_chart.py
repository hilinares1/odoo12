# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class FalProjectBudgetOrgChartController(http.Controller):
    _parent_child_level = 2  # FP request

    def _prepare_data(self, fal_project_budget):
        fal_project_budget_type = fal_project_budget.sudo().type
        return dict(
            id=fal_project_budget.id,
            name=fal_project_budget.name,
            link='/mail/view?model=fal.project.budget&res_id=%s' % fal_project_budget.id,
            fal_project_budget_type=fal_project_budget_type,
            direct_sub_count=len(fal_project_budget.child_ids),
            indirect_sub_count=fal_project_budget.child_all_count,
        )

    @http.route('/fal_project_budget/get_org_chart', type='json', auth='user')
    def get_org_chart(self, fal_project_budget_id):
        if not fal_project_budget_id:  # to check
            return {}
        fal_project_budget_id = int(fal_project_budget_id)

        Fal_Project_Budget = request.env['fal.project.budget']
        # check and raise
        if not Fal_Project_Budget.check_access_rights('read', raise_exception=False):
            return {}
        try:
            Fal_Project_Budget.browse(fal_project_budget_id).check_access_rule('read')
        except AccessError:
            return {}
        else:
            fal_project_budget = Fal_Project_Budget.browse(fal_project_budget_id)

        # compute project budget data for org chart
        ancestors, current = request.env['fal.project.budget'], fal_project_budget
        while current.parent_id:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self._prepare_data(fal_project_budget),
            parents=[self._prepare_data(ancestor) for idx, ancestor in enumerate(ancestors) if idx < self._parent_child_level],
            parents_more=len(ancestors) > self._parent_child_level,
            children=[self._prepare_data(child) for child in fal_project_budget.child_ids],
        )
        values['parents'].reverse()
        return values
