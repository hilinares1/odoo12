# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import Controller, request, route


class DigestController(Controller):

    @route('/kpi/<int:digest_id>/info', type='http', website=True, auth='user')
    def digest_info(self, digest_id, **post):
        digest = request.env['digest.digest'].sudo().browse(digest_id)
        user = request.env.user
        company = user.company_id
        data = digest.compute_kpis(company, user)
        kpi_actions = digest.compute_kpis_actions(company, user)
        tips = digest.compute_tips(company, user)
        return request.render('kpi_web.portal_digest_info', {
            'digest': digest,
            'data': data,
            'kpi_actions': kpi_actions,
            'tips': tips,
        })
