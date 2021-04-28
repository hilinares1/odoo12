from odoo import api, fields, models,_
from odoo.exceptions import except_orm, UserError, ValidationError
from datetime import datetime, timedelta
import datetime


class sales_man(models.Model):
    _name = "sales.man"
    

    name = fields.Many2one('res.users',string="Salesman")
    period_id = fields.One2many('saleman.period','saleper_id',string='Discount Periods')

    @api.constrains('period_id')
    def check_in_out_date(self):
        for line in self.period_id:
            if line.e_date and line.f_date:
                if line.e_date < line.f_date:
                    raise except_orm(_('Warning'), _('End Date \ should be greater than Begin date.'))
                if line.e_date == line.f_date:
                    raise except_orm(_('Warning'), _('End and Begin Date \ should not be equal , End date must to be greater'))

    
    @api.depends('name')
    def _name_sale(self):
        self.period_id.saleper_id = self.name

class saleman_period(models.Model):
    _name= "saleman.period"
    

    saleper_id = fields.Char(string="Salesman",invisible=True)
    target = fields.Float(' Monthly Sales Target')
    a_target = fields.Float('Actual Sales Amount')
    f_date =  fields.Date('Begin Date')
    e_date =  fields.Date('End Date')
    dis =  fields.Float('Available Discount')

class order_inherit(models.Model):
    _inherit = "sale.order"
    

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('approve', 'To Approve'),
        ('reject', 'Rejected'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    saleman = fields.Many2one('sales.man', string='Salesman',compute="_com_saleman")
    dtoday = fields.Date('current Date' , default=datetime.date.today())
    approve_date = fields.Date('Approve Date',invisible=True)

    @api.multi
    def _com_saleman(self):
        man = self.env['sales.man'].search([])
        for l in man:
            if l.name.name == self.env.user.name:
                self.saleman = l.id
        if not self.saleman:
            raise ValidationError(_('''You don't have Discout availablity and sales target yet, please ask your manager to add you!'''))

        
        


    @api.multi
    def ask_approve(self):
        return self.write({'state': 'approve'})

    @api.multi
    def button_reject(self):
        return self.write({'state': 'reject'})
    
    @api.multi
    def button_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def button_approve(self, force=False):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now(),
            'approve_date': fields.Date.context_today(self)
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()

        periods = {}
        periods = self.env['sales.man'].search([('id','=',self.saleman.id)])
        for l in periods.period_id:
            if (self.dtoday >= l.f_date) and (self.dtoday <= l.e_date):
                tar = l.a_target+ self.amount_total
                l.a_target = tar
        
        return True

    

    @api.multi
    def action_confirm(self):
        # approve discount part
        periods = {}
        periods = self.env['sales.man'].search([('id','=',self.saleman.id)])
        for l in periods.period_id:
            if (self.dtoday >= l.f_date) and (self.dtoday <= l.e_date):
                for line in self.order_line:
                    if l.dis >= line.discount:
                        continue
                    else:
                        raise except_orm(_('Warning'), _('This Discount is more than you can offer ask for approve: \ Please Click in button Ask for Approve to send approve to your manager'))
        # approve discount part

        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()

        periods = {}
        periods = self.env['sales.man'].search([('id','=',self.saleman.id)])
        for l in periods.period_id:
            if (self.dtoday >= l.f_date) and (self.dtoday <= l.e_date):
                tar = l.a_target+ self.amount_total
                l.a_target = tar
                # periods.update({'period_id': [(0, 0, {'a_target': tar})]})

        return True





    

