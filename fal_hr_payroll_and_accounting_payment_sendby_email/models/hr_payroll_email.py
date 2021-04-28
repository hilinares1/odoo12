from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


#PAYROLL EMAIL

class Sendbyemail(models.Model):

    _inherit='hr.payslip'

    @api.multi
    def send_payslip_by_email(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('fal_hr_payroll_and_accounting_payment_sendby_email', 'payslip_email_template')[1]
            #template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "fal_hr_payroll_and_accounting_payment_sendby_email.payslip_email_notification",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    #SUPPLIER EMAIL
class Sendbyemail_supplier(models.Model):

    _inherit='account.payment'

    company_name = fields.Char( string="Company Name")

    @api.multi
    def send_payment_by_email(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.company_name = self.company_id.name

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('fal_hr_payroll_and_accounting_payment_sendby_email', 'supplier_payment_mail_template')[1]
            #template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'account.payment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "fal_hr_payroll_and_accounting_payment_sendby_email.supplier_email_notification",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }