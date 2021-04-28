# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    fal_final_approval = fields.Char(
        string="Final Approval",
        help="Who has the final approval on the project?",
    )
    fal_industry = fields.Char(
        string="Industry",
        help="What Industry?",
    )
    fal_year = fields.Integer(
        string="Year Founded",
    )
    fal_employee_number = fields.Integer(
        string="Number Of Employee",
        help="How many employees",
    )
    fal_general_structure = fields.Char(
        string="General Structure",
        help="General structure of the company (WOFE, Trading in HK, ...)",
    )
    fal_group_company = fields.Text(
        string="Group Company?",
        help="If a group, how many companies? Where ?",
    )
    fal_contact = fields.Char(
        string="Preferred Contact",
        help="What is the preferred way to contact you ?",
    )
    fal_crm_line_ids = fields.One2many('crm.lead.line', 'fal_crm_line_id')  # line ide ke crmlead.line

    @api.multi
    def action_set_lost_and_link_partner(self):
        return {
            'name': _("Lost and Link Partner"),
            'view_mode': 'form',
            'view_id': self.env.ref('fal_crm_ext.view_crm_lead_lost_and_partner_binding').id,
            'view_type': 'form',
            'res_model': 'crm.lead.lost.and.partner.binding',
            'type': 'ir.actions.act_window',
            'domain': '[]',
            'context': {'active_id': self.id},
            'target': 'new',
        }


class CrmLeadLine(models.Model):
    _name = "crm.lead.line"
    _description = "Crm Lead line"

    fal_crm_line_id = fields.Many2one('crm.lead')  # field ke crm.lead
    fal_question = fields.Many2one('crm.lead.question', string='Question', required=True)  # ke question crm.lead.question
    fal_answer = fields.Many2one('crm.lead.answer', string="Answer")
    fal_custom_answer = fields.Text(string="Custom Answer")

    @api.onchange('fal_question')
    def onchange_many2one(self):
        if self.fal_question:
            ids = []
            for quest in self.fal_question.fal_crm_answer_ids:
                ids.append(quest.id)
            domain = [('id', 'in', ids)]
            return {'domain': {'fal_answer': domain}}


class CrmQuestion(models.Model):
    _name = "crm.lead.question"
    _rec_name = 'fal_question'
    _description = "Crm Question"

    @api.multi
    def name_get(self):
        res = []
        for questionid in self:
            res.append((questionid.id, "%s" % (questionid.fal_question)))
        return res

    fal_question = fields.Char(string="Question")
    fal_crm_answer_ids = fields.One2many('crm.lead.answer', 'fal_crm_answer_id', string='Answer')


class CrmAnswer(models.Model):
    _name = "crm.lead.answer"
    _rec_name = 'fal_answer'
    _description = "Crm Answer"

    @api.multi
    def name_get(self):
        res = []
        for answerid in self:
            res.append((answerid.id, "%s" % (answerid.fal_answer)))
        return res

    fal_crm_answer_id = fields.Many2one('crm.lead.question')
    fal_answer = fields.Char(string="Answer")
