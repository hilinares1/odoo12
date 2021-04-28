# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class ActivityReport(models.Model):
    """ SRM Proposal Analysis """

    _name = "srm.activity.report"
    _auto = False
    _description = "SRM Activity Analysis"
    _rec_name = 'id'

    date = fields.Datetime('Date', readonly=True)
    author_id = fields.Many2one('res.partner', 'Created By', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    team_id = fields.Many2one('srm.team', 'Purchase Team', readonly=True)
    proposal_id = fields.Many2one('srm.proposal', "Proposal", readonly=True)
    subject = fields.Char('Summary', readonly=True)
    subtype_id = fields.Many2one('mail.message.subtype', 'Subtype', readonly=True)
    mail_activity_type_id = fields.Many2one('mail.activity.type', 'Activity Type', readonly=True)
    country_id = fields.Many2one('res.country', 'Country', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    stage_id = fields.Many2one('srm.stage', 'Stage', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner/Vendor', readonly=True)
    proposal_type = fields.Char(
        string='Type',
        selection=[('proposal', 'Proposal'), ('agreement', 'Agreement')],
        help="Type is used to separate Proposals and Agreements")
    active = fields.Boolean('Active', readonly=True)
    probability = fields.Float('Probability', group_operator='avg', readonly=True)

    def _select(self):
        return """
            SELECT
                m.id,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.subject,
                l.id as proposal_id,
                l.user_id,
                l.team_id,
                l.country_id,
                l.company_id,
                l.stage_id,
                l.partner_id,
                l.type as proposal_type,
                l.active,
                l.probability
        """

    def _from(self):
        return """
            FROM mail_message AS m
        """

    def _join(self):
        return """
            JOIN srm_proposal AS l ON m.res_id = l.id
        """

    def _where(self):
        return """
            WHERE
                m.model = 'srm.proposal' AND m.mail_activity_type_id IS NOT NULL
        """

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where())
        )
