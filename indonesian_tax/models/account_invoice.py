# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    npwp = fields.Char(string='NPWP', size=15)
    ppkp = fields.Char(string='PPKP')
    gross = fields.Monetary(
        string='Gross Total',
        store=True, readonly=True, compute='_compute_amount')
    disc_total = fields.Monetary(
        string='Discount',
        store=True, readonly=True, compute='_compute_amount')
    nomor_faktur_pajak = fields.Char(string='Nomor Faktur Pajak', size=16)
    faktur_pajak_id = fields.Many2one('faktur.pajak', string='Faktur Pajak', copy=False)

    @api.multi
    def action_create_faktur(self):
        faktur_obj = self.env['faktur.pajak']
        today = fields.Date.context_today(self)

        for inv in self:
            if inv.type == 'out_invoice' and inv.faktur_pajak_id:
                vals = {
                    'date_used': today,
                    'invoice_id': inv.id,
                    'partner_id': inv.partner_id.id,
                    'pajak_type': 'out',
                    'dpp': inv.amount_untaxed or 0.0,
                    'tax_amount': inv.amount_tax or 0.0,
                    'currency_id': inv.currency_id.id,
                    'company_id': inv.company_id.id,
                }
                inv.faktur_pajak_id.write(vals)
                inv.faktur_pajak_id.sudo().used()
            if inv.type == 'in_invoice':
                if inv.nomor_faktur_pajak:
                    kode_transkasi = inv.nomor_faktur_pajak[:2]
                    categ = inv.nomor_faktur_pajak[2:3]
                    kode_cabang = inv.nomor_faktur_pajak[3:6]
                    tahun = inv.nomor_faktur_pajak[6:8]
                    nomor_fp = inv.nomor_faktur_pajak[-8:]
                    if len(inv.nomor_faktur_pajak) != 16:
                        raise ValidationError(_('Nomor faktur pajak tidak sesuai range referensi (16 digits)'))
                    if kode_transkasi not in ['01', '02', '03', '04', '05', '06', '07', '08', '09']:
                        raise ValidationError(_('Kode transkasi pada nomor faktur pajak tidak sesuai'))
                    if categ not in ['0', '1']:
                        raise ValidationError(_('Kode status pada nomor faktur pajak tidak sesuai'))
                    vals = {
                        'date_used': today,
                        'invoice_id': inv.id,
                        'partner_id': inv.partner_id.id,
                        'company_id': inv.company_id.id,
                        'pajak_type': 'in',
                        'dpp': inv.amount_untaxed or 0.0,
                        'tax_amount': inv.amount_tax or 0.0,
                        'currency_id': inv.currency_id.id,
                        'kode_transaksi': kode_transkasi,
                        'category': categ,
                        'nomor_urut': kode_cabang,
                        'tahun_penerbit': tahun,
                        'nomor_urut': nomor_fp,
                    }
                    if inv.faktur_pajak_id:
                        inv.faktur_pajak_id.write(vals)
                    else:
                        faktur = faktur_obj.create(vals)
                        inv.write({'faktur_pajak_id': faktur.id})
                        faktur.sudo().used()

    @api.multi
    def action_invoice_open(self):
        for inv in self:
            inv.action_create_faktur()
        res = super(AccountInvoice, self).action_invoice_open()
        return res

    def action_invoice_cancel(self):
        for inv in self:
            inv.faktur_pajak_id.cancel()
        res = super(AccountInvoice, self).action_invoice_cancel()
        return res

    def action_invoice_draft(self):
        for inv in self:
            inv.faktur_pajak_id.set_to_draft()
        return super(AccountInvoice, self).action_invoice_draft()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            self.npwp = self.partner_id.npwp
            if self.partner_id.pkp_status == 'pkp':
                self.ppkp = self.partner_id.ppkp
        return res
