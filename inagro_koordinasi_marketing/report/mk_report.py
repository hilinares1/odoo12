

from odoo import api, fields, models, tools
_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirm'),
    ('cancel', 'Cancel')
]


class MK_Report(models.Model):
    _name = "mk.report"
    _description = "Marketing Coordination Report"
    _auto = False
    # _order = 'date_order desc, price_total desc'

    facilities = fields.Many2one('facilities', string='Facilities',required=True)
    # date_request = fields.Date('Date Request Facilities', readonly=True, help="Date on which this document has been created", oldname='date')
    mk_number = fields.Char('Activity Number', readonly=True)
    qty_part = fields.Float('Facilities Participants', digits=(16, 0), readonly=True)
    customer = fields.Many2one('res.partner', 'Customer',readonly=True)
    customer_pic = fields.Char('Customer PIC',readonly=True)
    customer_contact = fields.Char('Customer Contact',readonly=True)
    tgl_mk = fields.Date('Date Request', readonly=True)
    mk_qty_part = fields.Float('Participants', digits=(16, 0), readonly=True)
    mk_qty_teacher = fields.Float('Teacher', digits=(16, 0), readonly=True)
    mk_mk_total = fields.Float('Total Participants', digits=(16, 0), readonly=True)
    qty_part = fields.Float('Facilities Participants', digits=(16, 0), readonly=True)
    mk_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel')
    ], 'State', readonly=True)
    user_id = fields.Many2one('res.users', 'User',readonly=True)
    department_id = fields.Many2one('hr.department', string='Divisi',readonly=True)
    name_act = fields.Many2one('ourdoor.activities', string='Name Activity',required=True)


    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            %s
            )""" 
            % (self._table, self._select(), self._from(), self._group_by()))

    def _select(self):
        select_str = """
            SELECT
                min(fl.id) as id,
                fl.name as facilities,
                mk.name AS mk_number,
                SUM ( fl.qty ) AS qty_part,
                mk.partner_id AS customer,
                mk.customer_pic,
                mk.customer_contact,
                mk.DATE AS tgl_mk,
                SUM ( mk.qty_participant ) AS mk_qty_part,
                SUM ( mk.qty_teacher ) AS mk_qty_teacher,
                SUM ( mk.qty_add_participant ) AS mk_qty_add_part,
                SUM ( mk.total ) AS mk_mk_total,
                mk.STATE AS mk_state,
                mk.user_id,
                mk.department_id,
                ac.name AS name_act
        """
        return select_str

    def _from(self):
        from_str = """
            facilities_line fl
            LEFT JOIN koordinasi_marketing mk ON fl.fcl_id = mk.ID
            LEFT JOIN activities_line ac ON mk.id = ac.act_id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                fl.NAME,
                mk.name,
                mk.partner_id,
                mk.customer_pic,
                mk.customer_contact,
                mk.DATE,
                mk.STATE,
                mk.user_id,
                mk.department_id,
                ac.name
        """
        return group_by_str
