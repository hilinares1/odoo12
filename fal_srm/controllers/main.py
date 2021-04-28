# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo.addons.mail.controllers.main import MailController
from odoo import http

_logger = logging.getLogger(__name__)


class CrmController(http.Controller):

    @http.route('/proposal/case_mark_won', type='http', auth='user', methods=['GET'])
    def srm_proposal_case_mark_won(self, res_id, token):
        comparison, record, redirect = MailController._check_token_and_record_or_redirect('srm.proposal', int(res_id), token)
        if comparison and record:
            try:
                record.action_set_won()
            except Exception:
                _logger.exception("Could not mark srm.proposal as won")
                return MailController._redirect_to_messaging()
        return redirect

    @http.route('/proposal/case_mark_lost', type='http', auth='user', methods=['GET'])
    def srm_proposal_case_mark_lost(self, res_id, token):
        comparison, record, redirect = MailController._check_token_and_record_or_redirect('srm.proposal', int(res_id), token)
        if comparison and record:
            try:
                record.action_set_lost()
            except Exception:
                _logger.exception("Could not mark crm.lead as lost")
                return MailController._redirect_to_messaging()
        return redirect

    @http.route('/proposal/convert', type='http', auth='user', methods=['GET'])
    def srm_proposal_convert(self, res_id, token):
        comparison, record, redirect = MailController._check_token_and_record_or_redirect('srm.proposal', int(res_id), token)
        if comparison and record:
            try:
                record.convert_opportunity(record.partner_id.id)
            except Exception:
                _logger.exception("Could not convert crm.lead to opportunity")
                return MailController._redirect_to_messaging()
        return redirect
