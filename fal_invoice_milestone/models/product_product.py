from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _search(
            self, args, offset=0, limit=None, order=None,
            count=False, access_rights_uid=None):
        context = self._context or {}
        # Return only service product if context is exist
        if context.get('search_default_services', False):
            args += [('type', '=', 'service')]

        return super(ProductProduct, self)._search(
            args, offset, limit, order, count=count,
            access_rights_uid=access_rights_uid)

# end of ProductProduct()
