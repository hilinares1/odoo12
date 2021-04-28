# -*- coding: utf-8 -*-

from odoo import api, fields, models


class easy_exporting_wizard(models.TransientModel):
    _name = "easy.exporting.wizard"
    _description = "Easy Exporting Wizard"

    model_id = fields.Many2one(
        'ir.model',
        'Object',
        required=True,
        ondelete='cascade',
        help="Select the object on which want to be download."
    )
    resource = fields.Char('Resource', size=128)
    template_id = fields.Many2one(
        'ir.exports',
        string='Template',
        required=True,
        help="Select the template on which want to be download."
    )
    filter_ids = fields.Many2many(
        'ir.filters',
        'easy_export_filter_rel',
        'easy_export_id',
        'filter_id',
        string='Filter',
        help="Select the filter on which want to be download."
    )
    from_date = fields.Date('From')
    to_date = fields.Date('To')
    temp = fields.Text('temp')
    temp_domain = fields.Text('Domain')
    temp_file = fields.Binary('File')
    temp_file_name = fields.Char('name', size=64)
    file_format = fields.Selection([
        ('Excel', 'Excel'),
        ('CSV', 'CSV')],
        string='File Format',
        required=True,
        default='Excel'
    )

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.resource = ''
        if self.model_id:
            self.resource = self.model_id.model

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            export = self.template_id
            temp_field = []
            for field in export.export_fields:
                temp_field.append(field.name)
            out = ','.join(temp_field)
            self.temp = out

    @api.onchange('filter_ids', 'from_date', 'to_date', 'resource')
    def onchange_filter_ids(self):
        out = ''
        temp_domain = []
        if self.filter_ids:
            for filter in self.filter_ids:
                for dom in eval(filter.domain):
                    temp_domain.append(dom)
        if self.from_date and self.to_date:
            resource_obj = self.env[self.resource]
            resource_fields = resource_obj.fields_get()
            if 'date' in resource_fields:
                temp_domain.append(['date', '>=', str(self.from_date)])
                temp_domain.append(['date', '<=', str(self.to_date)])
            else:
                temp_domain.append(['create_date', '>=', str(self.from_date)])
                temp_domain.append(['create_date', '<=', str(self.to_date)])
        out += str(temp_domain)
        self.temp_domain = out

# end of easy_exporting_wizard()
