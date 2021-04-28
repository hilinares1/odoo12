import datetime, requests
from odoo import models, fields, api


class Visits(models.Model):
    """
    This will create a table named crm_visits and add header base on the defined variables
    """
    _name = 'crm.visits'
    _description = 'Visit'
    _rec_name = 'itinerary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    itinerary = fields.Many2one('crm.lead', 'Itineray/Project Name',
                                required=True, track_visibility="always")
    customer = fields.Many2one('res.partner', 'Customer', related='itinerary.partner_id')
    start_date_time = fields.Datetime('Start Date/Time',
                                      default=datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                                      , track_visibility="always")
    end_date_time = fields.Datetime('End Date/Time',
                                    default=datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                                    , track_visibility="always")
    check_in_date_time = fields.Datetime('Check-in Date/Time', readonly=True)
    check_out_date_time = fields.Datetime('Check-out Date/Time', readonly=True)
    check_in_latitude = fields.Char('Check-in Latitude', readonly=True)
    check_in_longitude = fields.Char('Check-in Longitude', readonly=True)
    check_out_latitude = fields.Char('Check-out Latitude', readonly=True)
    check_out_longitude = fields.Char('Check-out Longitude', readonly=True)
    salesman = fields.Many2one('res.users', 'Salesman', ondelete='cascade', required=True,
                               default=lambda self: self.env.user, track_visibility="always")
    shope_type = fields.Char('Shope Type', track_visibility="always")
    key_objective_1 = fields.Char('1.Key Objectives', track_visibility="always")
    key_objective_2 = fields.Char('2.Key Objectives', track_visibility="always")
    key_objective_3 = fields.Char('3.Key Objectives', track_visibility="always")
    key_objective_4 = fields.Char('4.Key Objectives', track_visibility="always")
    internal_note = fields.Text('Internal Notes')
    state = fields.Selection([
        ('check-in', 'Check-In'),
        ('check-out', 'Check-Out'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled')], string="Status", default='check-in', readonly=True)
    status = fields.Char('Status', default='Open')

    def action_check_in(self):
        """
        This will be executed when check-in button is pressed
        This will update the fields base in the for loop

        :return: string, datetime
        """
        geolocation = requests.get('https://ipinfo.io')
        for rec in self:
            rec.state = 'check-out'
            rec.check_in_date_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            rec.check_in_latitude, rec.check_in_longitude = geolocation.json()['loc'].split(',')

    def action_check_out(self):
        """
        This will be executed when check-out button is pressed
        This will update the fields base in the for loop

        :return: string, datetime
        """
        geolocation = requests.get('https://ipinfo.io')
        for rec in self:
            rec.state = 'complete'
            rec.check_out_date_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            rec.check_out_latitude, rec.check_out_longitude = geolocation.json()['loc'].split(',')
            rec.status = 'Complete'

    def action_cancel(self):
        """
        This will be executed when cancel button pressed
        This will update the value inside state and status fields

        :return: string
        """
        for rec in self:
            rec.state = 'cancelled'
            rec.status = 'Cancelled'

    @api.model
    def default_get(self, fields):
        """
        The function will be called when pressing create button
        This will override the default_get() function
        Update itinerary base in active_id

        :param fields: list of all crm.visits fields
        :return: integer
        """
        res = super(Visits, self).default_get(fields)
        res['itinerary'] = self._context.get('active_id')
        return res


class Leads(models.Model):
    """
    This will extends the crm.lead
    """
    _inherit = 'crm.lead'

    visit_count = fields.Integer(compute='compute_count')  # Display counted visits in smart-button

    def compute_count(self):
        """
        This will count the visits base on active_id

        :return: integer
        """
        for record in self:
            record.visit_count = self.env['crm.visits'].search_count(
                [('itinerary', '=', self.id), ('create_uid', '=', self.env.user.id)])

    def crm_visits_smart_button(self):
        """
        This will be executed when the smart-button of the visits is pressed
        This will redirect to crm.visits form then display the view base on the **kwargs

        :return: dictionary(action)
        """
        self.ensure_one()  # check the record is singleton, if self contains multiple records, throw error!
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'view_mode': 'tree,form',
            'res_model': 'crm.visits',
            'domain': [('itinerary', '=', self.id), ('create_uid', '=', self.env.user.id)],
            # 'context': {"search_default_my_visit": 1},
        }
