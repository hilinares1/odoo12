# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GenerateFakturPajak(models.TransientModel):
    _name = 'generate.faktur.pajak'
    _description = "Generate Faktur Pajak"

    nomor_faktur_awal = fields.Char(string='Nomor Awal', size=20)
    nomor_faktur_akhir = fields.Char(string='Nomor Akhir', size=20)
    strip = fields.Char(string='Strip', size=3, default='-')
    dot = fields.Char(string='Dot', size=3, default='.')
    strip2 = fields.Char(string='Strip2', size=3, default='-')
    dot2 = fields.Char(string='Dot2', size=3, default='.')
    nomor_perusahaan = fields.Char(
        string='Nomor Perusahaan', size=3, required=True, default='010')
    kode_transaksi = fields.Char(
        string="Kode Cabang", size=3, required=True)
    nomor_awal = fields.Char(string='Nomor Faktur Awal', size=8, required=True)
    nomor_akhir = fields.Char(
        string='Nomor Faktur Akhir', size=8, required=True)
    tahun = fields.Char(
        string='Tahun Penerbit', size=2,
        required=True,
        default=lambda self: fields.Date.from_string(
            fields.Date.context_today(self)
        ).strftime('%y')
    )
    company_ids = fields.Many2many(
        'res.company', string='Allowed Companies')
    pajak_type = fields.Selection(
        [
            ('in', 'Faktur Pajak Masukan'),
            ('out', 'Faktur Pajak Keluaran')
        ], string='Type', default='out'
    )

    @api.multi
    def generate_faktur(self):
        for item in self:
            pajak_obj = self.env['faktur.pajak']
            awal = int(item.nomor_awal)
            akhir = int(item.nomor_akhir)
            while (awal <= akhir):
                company_list = []
                for comp in self.company_ids:
                    company_list.append((4, comp.id))
                vals = {
                    'nomor_perusahaan': item.nomor_perusahaan,
                    'tahun_penerbit': item.tahun,
                    'kode_cabang': item.kode_transaksi,
                    'nomor_urut': '%08d' % awal,
                    'state': '0',
                    'pajak_type': item.pajak_type,
                    'company_ids': company_list,
                }
                pajak_obj.create(vals)
                awal += 1
        return {'type': 'ir.actions.act_window_close'}
