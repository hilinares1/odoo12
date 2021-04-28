# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
from odoo.exceptions import UserError, AccessError
_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirm'),
    ('cancel', 'Cancel')
]

# class Room_marketing(models.Model):
#     _name = 'room.marketing'

#     name = fields.Char('Room Name', required=True)
#     capacity = fields.Integer('Capacity', required=True)

#     _sql_constraints = [('room_marketing_uniq', 'unique (name)', 'Name room must be unique!')]

class outdoor_activities(models.Model):
    _name = 'ourdoor.activities'

    name = fields.Char('Name',required=True)
    _sql_constraints = [('activities_uniq', 'unique (name)', 'Name must be unique!')]

    img_act_ids = fields.One2many('img.activities', 'act',
                               'Image Activities',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')
    tkhl_ids = fields.One2many('tkhl.activities', 'act',
                               'TKHL for Activities',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')

class image_activities(models.Model):

    _name = "img.activities"
    _description = "Image Activities"

    image = fields.Binary('Image', attachment=True,required=True)
    act = fields.Many2one('ourdoor.activities',
                                 'Activities',
                                 ondelete='cascade', readonly=True)

class tkhl_activities(models.Model):

    _name = "tkhl.activities"
    _description = "TKHL Activities"

    min_participants = fields.Float('Min Participants', digits=(16, 0))
    max_participants = fields.Float('Max Participants', digits=(16, 0))
    tkhl = fields.Float('TKHL', digits=(16, 0))
    act = fields.Many2one('ourdoor.activities',
                                 'Tkhl Activities',
                                 ondelete='cascade', readonly=True)


class facilities(models.Model):
    _name = 'facilities'

    name = fields.Char('Name',required=True)
    _sql_constraints = [('activities_uniq', 'unique (name)', 'Name must be unique!')]
    image = fields.Binary('Gambar')
    image2 = fields.Binary('Gambar2')
    # image3 = fields.Binary('Gambar3', attachment=True)
    # image4 = fields.Binary('Gambar4', attachment=True)
    # attachment = fields.Many2many("ir.attachment", string="Attachment")

    add_fcl_ids = fields.One2many('add.facilities', 'fcl',
                               'Additional Facilities',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')

    img_fcl_ids = fields.One2many('img.facilities', 'fcl',
                               'Additional Facilities',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')

class additional_facilities(models.Model):

    _name = "add.facilities"
    _description = "Additional Facilities"

    name = fields.Char(string='Name',required=True)
    qty = fields.Integer('Qty')
    fcl = fields.Many2one('facilities',
                                 'Facilities',
                                 ondelete='cascade', readonly=True)

class image_facilities(models.Model):

    _name = "img.facilities"
    _description = "Additional Facilities"

    image = fields.Binary('Image', attachment=True,required=True)
    fcl = fields.Many2one('facilities',
                                 'Facilities',
                                 ondelete='cascade', readonly=True)






# class food_beverage(models.Model):
#     _name = 'food.beverage'

#     name = fields.Char('Name')
#     _sql_constraints = [('food_uniq', 'unique (name)', 'Name must be unique!')]



class Koordinasi_marketing(models.Model):
    _name = 'koordinasi.marketing'
    _inherit = ['mail.thread']

    name = fields.Char('Activity Number', readonly=True)
    # tanggal = fields.Date('Date Request')
    partner_id = fields.Many2one('res.partner', 'Customer',
                                 index=True,
                                 required=True)
    customer_pic = fields.Char('Customer PIC',required=True)
    customer_contact = fields.Char('Customer Contact',required=True)

    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, oldname='creating_user_id')

    # employee_id = fields.Many2one('hr.employee', 'Emplopyee',
    #                              index=True,
    #                              track_visibility='onchange',
    #                              required=True)

    @api.one
    @api.depends('user_id')
    def _compute_department(self):
        if (self.user_id.id == False):
            self.department_id = None
            return

        employee = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)])
        # print(employee,' emp')
        if (len(employee) > 0):
            self.department_id = employee[0].department_id.id
        else:
            self.department_id = None

    department_id = fields.Many2one('hr.department', string='Divisi', compute='_compute_department', store=True,)

    date = fields.Date('Date Request',required=True)
    qty_participant = fields.Integer('Number of participants')
    qty_teacher = fields.Integer('Quantity Teacher')
    qty_add_participant = fields.Integer('Additional participants')
    total = fields.Integer('Total')

    state = fields.Selection(selection=_STATES,
                             string='State',
                             index=True,
                             required=True,
                             copy=False,
                             default='draft')

    @api.onchange('qty_participant', 'qty_teacher', 'qty_add_participant')
    def amount_total(self):
        # print('tes change')
        self.total = self.qty_participant+self.qty_teacher+self.qty_add_participant

    facilities_ids = fields.One2many('facilities.line', 'fcl_id',
                               'Facilities',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')

    activities_ids = fields.One2many('activities.line', 'act_id',
                               'Activities',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """

        # print('create')
        if not vals:
            vals = {}
        vals['name'] = self.env['ir.sequence'].next_by_code('koordinasi.marketing') or 'New'
        return super(Koordinasi_marketing, self).create(vals)


    @api.one
    def _get_flag_readonly(self):
        print(self.env.user.has_group('inagro_koordinasi_marketing.ga_koordinasi_marketing'),' has group')

        if self.state == 'draft':
            if self.create_uid == self.env.user:
                self.flag_readonly = 0
            elif self.env.user.has_group('inagro_koordinasi_marketing.ga_koordinasi_marketing') == True:
                self.flag_readonly = 0
            else:
                self.flag_readonly = 1
        else:
            self.flag_readonly = 1

        # print()
    flag_readonly = fields.Integer(string='Flag Readonly', store=False, compute = "_get_flag_readonly") 

    @api.multi
    def confirm_request(self):
        for fcl in self.facilities_ids:
            fcl.state = 'confirm'

        for act in self.activities_ids:
            act.state = 'confirm'
        return self.write({'state': 'confirm'})

    @api.multi
    def draft_request(self):
        for fcl in self.facilities_ids:
            fcl.state = 'draft'

        for act in self.activities_ids:
            act.state = 'draft'
        return self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        if self.create_uid != self.env.user or self.state != 'draft':
            raise UserError(_('You cannot delete this data !!!'))
        return super(Koordinasi_marketing, self).unlink()


class facilities_line(models.Model):

    _name = "facilities.line"
    _description = "Facilities Line"

    name = fields.Many2one('facilities', string='Name',required=True)
    qty = fields.Integer('Number of participants')
    start = fields.Datetime('Start')
    end = fields.Datetime('End')
    state = fields.Selection(selection=_STATES,
                             string='State',
                             index=True,
                             required=True,
                             copy=False,
                             default='draft')
    fcl_id = fields.Many2one('koordinasi.marketing',
                                 'MK Number',
                                 ondelete='cascade', readonly=True)
    date_request = fields.Date('Date Request', readonly=True,related='fcl_id.date',store=True)
    info = fields.Char('Information')


class activities_line(models.Model):

    _name = "activities.line"
    _description = "Activities Line"

    name = fields.Many2one('ourdoor.activities', string='Name',required=True)
    qty = fields.Integer('Number of participants')
    start = fields.Datetime('Start')
    end = fields.Datetime('End')
    tkhl = fields.Integer('TKHL')
    state = fields.Selection(selection=_STATES,
                             string='State',
                             index=True,
                             required=True,
                             copy=False,
                             default='draft')
    act_id = fields.Many2one('koordinasi.marketing',
                                 'MK Number',
                                 ondelete='cascade', readonly=True)
    date_request = fields.Date('Date Request', readonly=True,related='act_id.date',store=True)


    @api.model
    def create(self, vals):

        activities = self.env['ourdoor.activities'].search([('id', '=', int(vals.get('name')))]) 

        select = self.env.cr.execute("""select ac.row_number,ac.id,ac.min_participants,ac.max_participants,ac.tkhl
                                        from (
                                        select ROW_NUMBER () OVER (),id,min_participants,max_participants,tkhl
                                        from tkhl_activities
                                        where act = %s
                                        and (min_participants <= %s 
                                        and max_participants >= %s)
                                        order by id asc
                                        )as ac where ac.row_number = 1""",(int(vals.get('name')),int(vals.get('qty')),int(vals.get('qty'))))
        hasil = self.env.cr.fetchone()
        print(hasil,'data')
        if hasil == None:
            raise UserError(_('TKHL '+str(activities.name)+' is not set for '+str(vals.get('qty'))+' participants '))
        else:
            # print(round(hasil[4]),' master')
            # print(int(vals.get('tkhl')), 'trans')
            if int(vals.get('tkhl')) > round(hasil[4]):
                raise UserError(_('TKHL '+str(activities.name)+' max is '+str(round(hasil[4])) ))

        return super(activities_line, self).create(vals)


    @api.multi
    def write(self, vals):
        print (self.name,self.name.name)
        print(vals.get('tkhl'))
        print('tkhl 2 edit')

        qty = vals.get('qty') or self.qty
        tkhl= vals.get('tkhl') or self.tkhl

        print(qty,'qty')
        # exit() 

        select = self.env.cr.execute("""select ac.row_number,ac.id,ac.min_participants,ac.max_participants,ac.tkhl
                                        from (
                                        select ROW_NUMBER () OVER (),id,min_participants,max_participants,tkhl
                                        from tkhl_activities
                                        where act = %s
                                        and (min_participants <= %s 
                                        and max_participants >= %s)
                                        order by id asc
                                        )as ac where ac.row_number = 1""",(int(self.name),int(qty),int(qty)))
        hasil = self.env.cr.fetchone()
        print(hasil,'data')
        if hasil == None:
            raise UserError(_('TKHL '+str(self.name.name)+' is not set for '+str(qty)+' participants '))
        else:
            # print(round(hasil[4]),' master')
            # print(int(vals.get('tkhl')), 'trans')
            if int(tkhl) > round(hasil[4]):
                raise UserError(_('TKHL '+str(self.name.name)+' max is '+str(round(hasil[4])) ))

        return super(activities_line, self).write(vals)


