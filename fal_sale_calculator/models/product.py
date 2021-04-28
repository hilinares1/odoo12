from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    fal_is_computed_attribute = fields.Boolean(
        string='Price computed from the attribute',
        default=False
    )


class product_selector(models.TransientModel):
    _inherit = 'product.selector'

    added_price = fields.Float(string='Added Price', digits=dp.get_precision('Product Unit of Measure'), default=0.0)


class product_selector_line(models.TransientModel):
    _inherit = 'product.selector.line'

    custom_value = fields.Float(string='Product Attribute Custom Value(s)', digits=dp.get_precision('Product Unit of Measure'), default=0.0)

    @api.onchange('custom_value')
    def onchange_custom_value(self, val):
        self.custom_value = val

    @api.onchange('fal_available_value_ids', 'atribute_id', 'custom_value')
    def fal_available_value_ids_change(self):
        res = super(product_selector_line, self).fal_available_value_ids_change()
        attrval = self.fal_available_value_ids
        customval = self.custom_value
        val = self.value_id
        # customval = self.env['product.attribute.custom.value'].search([('attribute_value_id', '=', val.id)])
        localdict = dict({'attrval': attrval, 'customval': customval})
        localdict['result'] = None
        amount = 0.0
        if val.fal_is_computed_attribute is True:
            if val.amount_select == 'fix':
                try:
                    amount = val.amount_fix
                except:
                    raise UserError(_('Wrong quantity defined for %s.') % (val.name))
            elif val.amount_select == 'percentage':
                try:
                    amount = val.amount_percentage_base * (val.amount_percetage/100)
                except:
                    raise UserError(_('Wrong percentage base or quantity defined for %s.') % (val.name))
            else:
                try:
                    safe_eval(val.amount_python_compute, localdict, mode='exec', nocopy=True)
                    amount = localdict['result']
                except:
                    raise UserError(_('Wrong python code defined for %s.') % (val.name))
        for ps in self.product_selector_id:
            ps.added_price += amount
        return res


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    quantity = fields.Char(default='1.0',
        help="It is used in computation for percentage and fixed amount. "
             "For e.g. A rule for Meal Voucher having fixed amount of "
             u"1€ per worked day can have its quantity defined in expression "
             "like worked_days.WORK100.number_of_days.")
    amount_select = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
    ], string='Amount Type', index=True, required=True, default='fix', help="The computation method for the product attribute.")
    amount_fix = fields.Float(string='Fixed Amount', digits=dp.get_precision('Payroll'))
    amount_percentage = fields.Float(string='Percentage (%)', digits=dp.get_precision('Payroll Rate'),
        help='For example, enter 50.0 to apply a percentage of 50%')
    amount_python_compute = fields.Text(string='Python Code',
        default='''
                    # Available variables:
                    #----------------------
                    # attrval: product.attribute.value object
                    # customval: input custom value from product attribute value
                    # Note: returned value have to be set in the variable 'result'
                    result = attrval.name''')
    amount_percentage_base = fields.Char(string='Percentage based on', help='result will be affected to a variable')
    fal_is_computed_attribute = fields.Boolean(
        string='Computed Value',
        default=False
    )
