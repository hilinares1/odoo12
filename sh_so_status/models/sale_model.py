# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api

class sale_order(models.Model):
    _inherit="sale.order"
    
    sh_fully_delivered=fields.Boolean(string="Delivered",readonly=True,default=False)
    sh_partially_delivered=fields.Boolean(string="Partially Delivered",readonly=True,default=False)
    sh_fully_paid=fields.Boolean(string="Paid",readonly=True,default=False)
    sh_partially_paid=fields.Boolean(string="Partially Paid",readonly=True,default=False)
    sh_hidden_compute_field=fields.Boolean(string="Hidden Compute",readonly=True,compute="check_delivery")
    
    @api.multi
    @api.depends('order_line.qty_delivered')    
    def check_delivery(self):
        if self:
            for so_rec in self:
                if so_rec.order_line:
                    no_service_product_line=so_rec.order_line.filtered(lambda line: (line.product_id) and (line.product_id.type != 'service'))
                    if no_service_product_line:
                        so_rec.write({'sh_partially_delivered':False})
                        so_rec.write({'sh_fully_delivered':False})                        
                        product_uom_qty = qty_delivered = 0
                        for line in no_service_product_line:
                            qty_delivered += line.qty_delivered
                            product_uom_qty += line.product_uom_qty
                        if product_uom_qty == qty_delivered:
                            so_rec.sh_fully_delivered=True
                            so_rec.write({'sh_fully_delivered':True})                            
                        elif product_uom_qty > qty_delivered and qty_delivered!=0.0:
                            so_rec.sh_partially_delivered=True
                            so_rec.write({'sh_partially_delivered':True})

                            
        
        
                if so_rec.invoice_ids:
                    sum_of_invoice_amount=0.0
                    sum_of_due_amount=0.0
                    so_rec.write({'sh_fully_paid':False}) 
                    so_rec.write({'sh_partially_paid':False})   
                    for invoice_id in so_rec.invoice_ids.filtered(lambda inv: inv.state not in ['cancel','draft']):
                        sum_of_invoice_amount=sum_of_invoice_amount + invoice_id.amount_total_signed
                        sum_of_due_amount=sum_of_due_amount + invoice_id.residual_signed  
                        if invoice_id.residual_signed != 0 and invoice_id.residual_signed < invoice_id.amount_total_signed:
                            so_rec.sh_partially_paid=True
                            so_rec.write({'sh_partially_paid':True})                      
                        
                    if sum_of_due_amount == 0 and sum_of_invoice_amount >= so_rec.amount_total:
                        so_rec.write({'sh_fully_paid':True})     

