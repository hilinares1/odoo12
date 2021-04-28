##############################################################################
#
#    Copyright (C) 2011 ADSOFT OpenERP Partner Indonesia
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models, _
#from openerp import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

# try:
#     import phonenumbers
# except Exception as e:
#     _logger.warning(
#         'Import Error for phonenumbers, you will not be able to validate phone number.\n'
#         'Consider Installing phonenumbers or dependencies: https://pypi.python.org/pypi/phonenumbers/7.2.6.')
#     raise e

class res_country_state(models.Model):
    _inherit = "res.country.state"
    
    #name = fields.Char(string='Province')
    kabupaten_line = fields.One2many('res.kabupaten', 'state_id', string='Kabupaten')

class ResKabupaten(models.Model):
    _name = "res.kabupaten"
    _description = "List Kabupaten"
    
    name = fields.Char(string='Kabupaten')
    state_id = fields.Many2one('res.country.state', string="Province")
    kecamatan_line = fields.One2many('res.kecamatan', 'kabupaten_id', string='Kecamatan')
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # TDE FIXME: strange
        if self._context.get('search_default_province'):
            args += [('state_id', '=', self._context['search_default_province'])]
        return super(ResKabupaten, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    
class ResKecamatan(models.Model):
    _name = "res.kecamatan"
    _description = "List Kecamatan"
    
    name = fields.Char(string='Kecamatan')
    state_id = fields.Many2one('res.country.state', string="Province")
    kabupaten_id = fields.Many2one('res.kabupaten', string="Kabupaten")
    kelurahan_line = fields.One2many('res.kelurahan', 'kecamatan_id', string='Kelurahan')
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # TDE FIXME: strange
        if self._context.get('search_default_kabupaten'):
            args += [('kabupaten_id', '=', self._context['search_default_kabupaten'])]
        if self._context.get('search_default_province'):
            args += [('state_id', '=', self._context['search_default_province'])]
        return super(ResKecamatan, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    

class ResKelurahan(models.Model):
    _name = "res.kelurahan"
    _description = "List Kelurahan"
    
    name = fields.Char(string='Kelurahan')
    state_id = fields.Many2one('res.country.state', string="Province")
    kabupaten_id = fields.Many2one('res.kabupaten', string="Kabupaten")
    kecamatan_id = fields.Many2one('res.kecamatan', string="Kecamatan")
    zip = fields.Char("Kode Post")
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # TDE FIXME: strange
        if self._context.get('search_default_zip'):
            args += [('zip', '=', self._context['search_default_zip'])]
        if self._context.get('search_default_kecamatan'):
            args += [('kecamatan_id', '=', self._context['search_default_kecamatan'])]
        if self._context.get('search_default_kabupaten'):
            args += [('kabupaten_id', '=', self._context['search_default_kabupaten'])]
        if self._context.get('search_default_province'):
            args += [('state_id', '=', self._context['search_default_province'])]
        return super(ResKelurahan, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


class res_race(models.Model):
    _name = "res.race"
    _description = "List RAS/Suku"
    name = fields.Char(string='RAS', required=True , translate=True)

class res_religion(models.Model):
    _name = "res.religion"
    _description = "List Agama"
    
    name = fields.Char(string='Religion', required=True , translate=True)
