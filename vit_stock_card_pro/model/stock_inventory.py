from odoo import fields, api, models

class StockInventory(models.Model):
	_inherit = 'stock.inventory'

	saldo_awal = fields.Boolean(string='Saldo Awal')
	